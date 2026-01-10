from pathlib import Path

from pit8c.brokers import freedom24
from pit8c.brokers.base import BrokerAdapter, SupportedBroker
from pit8c.exceptions import Pit8cError
from pit8c.exchange.rates import fill_exchange_rates
from pit8c.io.xlsx import read_trades_from_xlsx, write_closed_positions_to_xlsx
from pit8c.models import ClosedPosition, Trade
from pit8c.positions.profit_calculator import calculate_profit
from pit8c.positions.trades_matcher import match_trades_fifo
from pit8c.reports.pit_8c import generate_pit_8c


def _get_broker_adapter(broker: SupportedBroker) -> BrokerAdapter:
    """Return the adapter implementation for the given broker enum."""
    match broker:
        case SupportedBroker.freedom24:
            return freedom24.Freedom24Adapter()
        case _:
            raise Pit8cError(f"Broker '{broker}' not supported yet")


def _list_xlsx_inputs(reports_path: Path) -> list[Path]:
    """Return report XLSX paths from a single file or a directory."""
    reports_path = reports_path.resolve()
    if reports_path.is_file():
        return [reports_path]
    if not reports_path.is_dir():
        raise Pit8cError(f"'{reports_path}' does not exist")

    files = sorted(
        p for p in reports_path.iterdir() if p.is_file() and p.suffix.lower() == ".xlsx" and not p.name.startswith("~$")
    )
    if not files:
        raise Pit8cError(f"No .xlsx files found in '{reports_path}'")
    return files


def load_trades_from_reports_path(adapter: BrokerAdapter, reports_path: Path) -> list[Trade]:
    """Read one or more report XLSX files and parse them into a unified list of trades."""
    trades: list[Trade] = []
    for xlsx_path in _list_xlsx_inputs(reports_path):
        raw_data = read_trades_from_xlsx(xlsx_path)
        parsed = adapter.parse_trades(raw_data)
        trades.extend(parsed)

    if not trades:
        raise Pit8cError(f"'{reports_path}' does not contain any trades")
    return trades


def match_trades_and_select_tax_year(trades: list[Trade], tax_year: int) -> list[ClosedPosition]:
    """Match trades using FIFO and return positions closed (sold) in the given tax year."""
    closed_positions = match_trades_fifo(trades)
    return [cp for cp in closed_positions if cp.sell_date.year == tax_year]


def process_reports_for_tax_year(broker: SupportedBroker, reports_path: Path, tax_year: int) -> None:
    # determine the proper adapter
    adapter = _get_broker_adapter(broker)

    # read report(s) and convert raw data into a unified structure
    trades = load_trades_from_reports_path(adapter, reports_path)

    # apply FIFO logic across all provided years, then select only positions closed in the requested tax year
    closed_positions = match_trades_and_select_tax_year(trades, tax_year)

    # fill exchange rates
    fill_exchange_rates(closed_positions)

    # calculate income and costs
    profit_positions, loss_positions = calculate_profit(closed_positions)

    # print PIT-8C
    output_dir = reports_path.parent if reports_path.is_file() else reports_path
    output_stem = reports_path.stem if reports_path.is_file() else reports_path.name
    output_base = f"{output_stem}_{tax_year}"
    pit_8c_path = output_dir / f"{output_base}_pit_8c.pdf"
    generate_pit_8c(closed_positions, pit_8c_path)

    # write the result to XLSX
    closed_positions_path = output_dir / f"{output_base}_closed_positions.xlsx"
    write_closed_positions_to_xlsx(profit_positions, loss_positions, closed_positions_path)

    print(f"Done! Generated PIT-8C to '{pit_8c_path}' and saved closed positions to '{closed_positions_path}'")
