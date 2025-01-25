from pathlib import Path

import typer

from pit38.brokers.base import SupportedBroker
from pit38.main import process_annual_report

app = typer.Typer()


@app.command("main")
def main(
    broker: SupportedBroker = typer.Argument(..., help="Broker name"),
    tax_report_file: Path = typer.Argument(..., help="Path to the annual tax report from your broker"),
):
    """
    Process the annual tax report using the specified broker adapter,
    reading tax_report_file and generating PIT-8C and .xlsx file with all closed positions (for audit).
    """
    process_annual_report(broker, tax_report_file)


if __name__ == "__main__":
    app()
