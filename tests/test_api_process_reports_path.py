from decimal import Decimal
from pathlib import Path

import openpyxl
from pit8c import Pit8c
from pit8c.exchange.provider import ExchangeRatesProvider


class _DummyProvider:
    def prefetch(self, years: set[int], currencies: set[str]) -> None:
        """Ignore prefetch requests and serve deterministic rates."""

        _ = years
        _ = currencies

    def get_rate(self, _d: object, _currency: str, *, use_previous_day: bool = True) -> Decimal:
        """Return a constant USD rate for tests (previous-day flag ignored)."""

        _ = use_previous_day
        return Decimal(1)


def _write_freedom24_report(path: Path) -> None:
    """Write a minimal Freedom24-like annual report XLSX file."""

    wb = openpyxl.Workbook()
    ws = wb.active

    headers = [
        "ISIN",
        "Ticker",
        "Direction",
        "Currency",
        "Settlement date",
        "Quantity",
        "Amount",
        "Price",
        "Commission",
        "Trade#",
    ]
    ws.append(headers)
    ws.append(
        [
            "X123",
            "X",
            "Buy",
            "USD",
            "2024-01-10",
            1,
            100,
            100,
            "0USD",
            1,
        ]
    )
    ws.append(
        [
            "X123",
            "X",
            "Sell",
            "USD",
            "2024-06-01",
            1,
            120,
            120,
            "0USD",
            2,
        ]
    )
    wb.save(path)


def test_process_reports_path_writes_xlsx_artifact(tmp_path: Path) -> None:
    provider: ExchangeRatesProvider = _DummyProvider()
    output_dir = tmp_path / "out"
    pit8c = Pit8c(
        broker="freedom24", exchange_provider=provider, output_dir=output_dir, write_pdf=False, write_xlsx=True
    )

    report_path = tmp_path / "annual_report_2024.xlsx"
    _write_freedom24_report(report_path)

    result = pit8c.process_reports_path(reports_path=report_path, tax_year=2024)
    assert result.input_reports == [report_path.resolve()]
    assert result.artifacts.closed_positions_xlsx_path is not None
    assert result.artifacts.closed_positions_xlsx_path.exists()
    assert result.artifacts.closed_positions_xlsx_path.parent == output_dir.resolve()
    assert result.artifacts.closed_positions_xlsx_path.name.endswith("_2024_closed_positions.xlsx")
