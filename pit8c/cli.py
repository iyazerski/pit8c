from pathlib import Path

import typer
from rich.console import Console

from pit8c.brokers.base import SupportedBroker
from pit8c.exceptions import Pit8cError
from pit8c.main import process_reports_for_tax_year

app = typer.Typer(pretty_exceptions_show_locals=False)
err_console = Console(stderr=True)

BROKER_ARG = typer.Argument(..., help="Broker name")
REPORTS_PATH_ARG = typer.Argument(
    ...,
    help="Path to the annual tax report (.xlsx) or a directory with multiple annual reports (.xlsx)",
)


@app.command("main")
def main(
    broker: SupportedBroker = BROKER_ARG,
    reports_path: Path = REPORTS_PATH_ARG,
    year: int = typer.Option(..., "--year", "-y", help="Tax year to calculate PIT-8C for (based on sell date year)"),
) -> None:
    """
    Process the annual tax report using the specified broker adapter,
    reading reports_path and generating PIT-8C and .xlsx file with all closed positions (for audit).
    """
    try:
        process_reports_for_tax_year(broker, reports_path, year)
    except Pit8cError as e:
        err_console.print(str(e))
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
