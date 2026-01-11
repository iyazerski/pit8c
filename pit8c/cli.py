from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pit8c.brokers.base import SupportedBroker
from pit8c.exceptions import Pit8cError
from pit8c.main import process_reports_for_tax_year

app = typer.Typer(pretty_exceptions_show_locals=False)
err_console = Console(stderr=True)


@app.command("main")
def main(
    broker: Annotated[SupportedBroker, typer.Option(..., help="Broker name")],
    reports_path: Annotated[
        Path,
        typer.Option(
            ..., help="Path to the annual tax report (.xlsx) or a directory with multiple annual reports (.xlsx)"
        ),
    ],
    year: Annotated[int, typer.Option(..., help="Tax year to calculate PIT-8C for")],
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
