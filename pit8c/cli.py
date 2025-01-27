from pathlib import Path

import typer
from rich.console import Console

from pit8c.brokers.base import SupportedBroker
from pit8c.exceptions import pit8cException
from pit8c.main import process_annual_report

app = typer.Typer(pretty_exceptions_show_locals=False)
err_console = Console(stderr=True)


@app.command("main")
def main(
    broker: SupportedBroker = typer.Argument(..., help="Broker name"),
    tax_report_file: Path = typer.Argument(..., help="Path to the annual tax report from your broker"),
):
    """
    Process the annual tax report using the specified broker adapter,
    reading tax_report_file and generating PIT-8C and .xlsx file with all closed positions (for audit).
    """
    try:
        process_annual_report(broker, tax_report_file)
    except pit8cException as e:
        err_console.print(str(e))
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
