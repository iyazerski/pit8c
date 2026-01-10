from pathlib import Path

import typer
from rich.console import Console

from pit8c.brokers.base import SupportedBroker
from pit8c.exceptions import Pit8cError
from pit8c.main import process_annual_report

app = typer.Typer(pretty_exceptions_show_locals=False)
err_console = Console(stderr=True)

BROKER_ARG = typer.Argument(..., help="Broker name")
TAX_REPORT_FILE_ARG = typer.Argument(..., help="Path to the annual tax report from your broker")


@app.command("main")
def main(
    broker: SupportedBroker = BROKER_ARG,
    tax_report_file: Path = TAX_REPORT_FILE_ARG,
) -> None:
    """
    Process the annual tax report using the specified broker adapter,
    reading tax_report_file and generating PIT-8C and .xlsx file with all closed positions (for audit).
    """
    try:
        process_annual_report(broker, tax_report_file)
    except Pit8cError as e:
        err_console.print(str(e))
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
