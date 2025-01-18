import typer

from pit38.main import process_annual_report

app = typer.Typer(help="A CLI tool that assists in preparing the PIT-38 declaration.")


@app.command("process")
def process_command(
    broker: str = typer.Argument(..., help="Broker name (e.g. freedom24)"),
    input_file: str = typer.Argument(..., help="Path to the XLSX input file from your broker"),
    output_file: str = typer.Argument(..., help="Output XLSX file where results will be saved"),
):
    """
    Process the annual tax report using the specified BROKER adapter,
    reading INPUT_FILE and writing to OUTPUT_FILE in the standardized format.
    """
    process_annual_report(broker, input_file, output_file)


if __name__ == "__main__":
    app()
