from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from pit38.models import ClosedPosition

TEMPLATES_DIR = Path(__file__).parent / "templates"
PIT_8C_TXT = TEMPLATES_DIR / "PIT-8C.txt"
PIT_8C_PDF = TEMPLATES_DIR / "PIT-8C.pdf"


def generate_pit_8c(closed_positions: list[ClosedPosition], file: Path) -> None:
    total_income = Decimal("0.0")
    total_costs = Decimal("0.0")
    for cp in closed_positions:
        total_income += cp.income_pln
        total_costs += cp.costs_pln
    net_income = total_income - total_costs

    # print txt version of PIT-8C to console
    pit_8c_template = PIT_8C_TXT.read_text().strip()
    print(pit_8c_template.format(total_income=str(total_income), costs=str(total_costs), net_income=str(net_income)))

    # Load PDF
    reader = PdfReader(PIT_8C_PDF)
    writer = PdfWriter()

    # Data mapping (field names must match PDF form fields)
    data = {"total_income": str(total_income), "total_costs": str(total_costs), "net_income": str(net_income)}

    # Copy pages and update form fields
    for page in reader.pages:
        writer.add_page(page)

    # Update fields on the first page (adjust if fields are on other pages)
    writer.update_page_form_field_values(writer.pages[0], data)

    # Save filled PDF
    with open(file, "wb") as f:
        writer.write(f)
