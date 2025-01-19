from pathlib import Path

from pit38.brokers import freedom24
from pit38.exchange.rates import fill_exchange_rates
from pit38.io.xlsx import read_trades_from_xlsx, write_trades_to_xlsx
from pit38.positions.trades_matcher import match_trades_fifo


def process_annual_report(broker_name: str, input_file: Path, output_file: Path) -> None:
    # determine the proper adapter
    if broker_name.lower() == "freedom24":
        adapter = freedom24.Freedom24Adapter()
    else:
        raise ValueError(f"Broker '{broker_name}' not supported yet.")

    # read annual tax report (trades) from XLSX
    raw_data = read_trades_from_xlsx(input_file.resolve().as_posix())

    # convert raw data into a unified structure
    trades = adapter.parse_trades(raw_data)

    # apply FIFO logic
    closed_positions = match_trades_fifo(trades)

    # fill exchange rates
    fill_exchange_rates(closed_positions)

    # write the result to XLSX
    write_trades_to_xlsx(closed_positions, output_file.resolve().as_posix())

    print(f"Done! Wrote closed positions to '{output_file}'")
