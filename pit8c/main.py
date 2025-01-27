from pathlib import Path

from pit8c.brokers import freedom24
from pit8c.brokers.base import SupportedBroker
from pit8c.exceptions import pit8cException
from pit8c.exchange.rates import fill_exchange_rates
from pit8c.io.xlsx import read_trades_from_xlsx, write_closed_positions_to_xlsx
from pit8c.positions.profit_calculator import calculate_profit
from pit8c.positions.trades_matcher import match_trades_fifo
from pit8c.reports.pit_8c import generate_pit_8c


def process_annual_report(broker: SupportedBroker, tax_report_file: Path) -> None:
    # determine the proper adapter
    match broker:
        case SupportedBroker.freedom24:
            adapter = freedom24.Freedom24Adapter()
        case _:
            raise pit8cException(f"Broker '{broker}' not supported yet")

    # read annual tax report (trades) from XLSX
    tax_report_file = tax_report_file.resolve()
    if not tax_report_file.exists():
        raise pit8cException(f"'{tax_report_file}' does not exist")
    raw_data = read_trades_from_xlsx(tax_report_file)

    # convert raw data into a unified structure
    trades = adapter.parse_trades(raw_data)
    if not trades:
        raise pit8cException(f"'{tax_report_file}' does not contain any trades")

    # apply FIFO logic
    closed_positions = match_trades_fifo(trades)
    if not closed_positions:
        raise pit8cException(f"'{tax_report_file}' does not contain any closed positions")

    # fill exchange rates
    fill_exchange_rates(closed_positions)

    # calculate income and costs
    profit_positions, loss_positions = calculate_profit(closed_positions)

    # print PIT-8C
    pit_8c_path = tax_report_file.parent / f"{tax_report_file.stem}_pit_8c.pdf"
    generate_pit_8c(closed_positions, pit_8c_path)

    # write the result to XLSX
    closed_positions_path = tax_report_file.parent / f"{tax_report_file.stem}_closed_positions.xlsx"
    write_closed_positions_to_xlsx(profit_positions, loss_positions, closed_positions_path)

    print(f"Done! Generated PIT-8C to '{pit_8c_path}' and saved closed positions to '{closed_positions_path}'")
