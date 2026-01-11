from pathlib import Path
from typing import Annotated

import typer

from pit8c.api import Pit8c
from pit8c.brokers.base import SupportedBroker
from pit8c.exceptions import Pit8cError

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback(invoke_without_command=True)
def main(
    broker: Annotated[SupportedBroker, typer.Option(..., help="Broker name")],
    reports_path: Annotated[
        Path, typer.Option(..., help="Path to annual report (.xlsx) or a directory with multiple annual reports")
    ],
    year: Annotated[int, typer.Option(..., "--year", "-y", help="Tax year to calculate PIT-8C for")],
) -> None:
    """
    Process the annual tax report using the specified broker adapter,
    reading reports_path and generating PIT-8C and .xlsx file with all closed positions (for audit).
    """
    try:
        pit8c = Pit8c(broker=broker)
        result = pit8c.process_reports_path(reports_path=reports_path, tax_year=year)

        if result.artifacts.pit8c_text:
            typer.echo(result.artifacts.pit8c_text)

        if result.artifacts.pit8c_pdf_path is not None and result.artifacts.closed_positions_xlsx_path is not None:
            typer.echo(
                "Done! Generated PIT-8C to "
                f"'{result.artifacts.pit8c_pdf_path}' and saved closed positions to '{result.artifacts.closed_positions_xlsx_path}'"
            )
    except Pit8cError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
