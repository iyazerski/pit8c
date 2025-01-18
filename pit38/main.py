from pit38.brokers import freedom24
from pit38.trades_finder import match_trades_fifo
from pit38.xlsx_io import read_trades_from_xlsx, write_trades_to_xlsx


def process_annual_report(broker_name: str, input_file: str, output_file: str) -> None:
    # determine the proper adapter
    if broker_name.lower() == "freedom24":
        adapter = freedom24.Freedom24Adapter()
    else:
        raise ValueError(f"Broker '{broker_name}' not supported yet.")

    # read annual tax report (trades) from XLSX
    raw_data = read_trades_from_xlsx(input_file)

    # convert raw data into a unified structure
    trades = adapter.parse_trades(raw_data)

    # apply FIFO logic
    closed_positions = match_trades_fifo(trades)

    # write the result to XLSX
    write_trades_to_xlsx(closed_positions, output_file)

    print(f"Done! Wrote closed positions to '{output_file}'")
