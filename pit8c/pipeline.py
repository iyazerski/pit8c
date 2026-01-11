from pathlib import Path

from pit8c.brokers.base import BrokerAdapter
from pit8c.exceptions import Pit8cError
from pit8c.io.xlsx import read_trades_from_xlsx
from pit8c.models import ClosedPosition, Trade
from pit8c.positions.trades_matcher import match_trades_fifo


def list_xlsx_inputs(reports_path: Path) -> list[Path]:
    """Return report XLSX paths from a single file path or a directory containing XLSX files."""

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


def load_trades_from_reports_path(adapter: BrokerAdapter, reports_path: Path) -> tuple[list[Path], list[Trade]]:
    """Read one or more report XLSX files and parse them into a unified list of trades."""

    input_reports = list_xlsx_inputs(reports_path)

    trades: list[Trade] = []
    for xlsx_path in input_reports:
        raw_data = read_trades_from_xlsx(xlsx_path)
        parsed = adapter.parse_trades(raw_data)
        trades.extend(parsed)

    if not trades:
        raise Pit8cError(f"'{reports_path}' does not contain any trades")
    return input_reports, trades


def match_trades_and_select_tax_year(trades: list[Trade], tax_year: int) -> list[ClosedPosition]:
    """Match trades using FIFO and return positions closed (sold) in the given tax year."""

    closed_positions = match_trades_fifo(trades)
    return [cp for cp in closed_positions if cp.sell_date.year == tax_year]
