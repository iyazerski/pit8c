from pathlib import Path
from typing import Protocol

from pypdf import PdfReader, PdfWriter

from pit8c.result import Pit8cTotals

TEMPLATES_DIR = Path(__file__).parent / "templates"
PIT_8C_TXT = TEMPLATES_DIR / "PIT-8C.txt"
PIT_8C_PDF = TEMPLATES_DIR / "PIT-8C.pdf"


class Pit8cReportGenerator(Protocol):
    """Generates human-readable text and optional PDF artifacts for PIT-8C totals."""

    def render_text(self, totals: Pit8cTotals) -> str:
        """Render PIT-8C text representation for console output."""

    def write_pdf(self, totals: Pit8cTotals, file: Path) -> None:
        """Write a filled PIT-8C PDF file to the provided path."""


class TemplatePit8cReportGenerator:
    """PIT-8C report generator based on shipped text and PDF templates."""

    def render_text(self, totals: Pit8cTotals) -> str:
        """Render PIT-8C text from template using aggregated totals."""

        pit_8c_template = PIT_8C_TXT.read_text().strip()
        return pit_8c_template.format(
            total_income=str(totals.income_pln),
            costs=str(totals.costs_pln),
            profit=str(totals.profit_pln),
        )

    def write_pdf(self, totals: Pit8cTotals, file: Path) -> None:
        """Fill PIT-8C PDF template with totals and write it to disk."""

        reader = PdfReader(PIT_8C_PDF)
        writer = PdfWriter()

        fields = {"35_income": str(totals.income_pln), "36_costs": str(totals.costs_pln)}
        if totals.is_profit:
            fields["37_profit"] = str(totals.profit_pln)
        else:
            fields["38_loss"] = str(abs(totals.profit_pln))

        writer.clone_reader_document_root(reader)
        writer.update_page_form_field_values(writer.pages[0], fields)

        with file.open("wb") as f:
            writer.write(f)
