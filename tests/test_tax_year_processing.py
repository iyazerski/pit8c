from pathlib import Path

import openpyxl
import pytest
from pit8c.brokers.freedom24 import Freedom24Adapter
from pit8c.exceptions import Pit8cError
from pit8c.main import load_trades_from_reports_path, match_trades_and_select_tax_year


def _write_freedom24_report(path: Path, rows: list[dict[str, object]]) -> None:
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
    for row in rows:
        ws.append([row.get(h) for h in headers])
    wb.save(path)


def test_tax_year_selection_works_with_cross_year_positions(tmp_path: Path) -> None:
    """FIFO matching uses prior-year buys while report includes only closures in the requested year."""
    report_2024 = tmp_path / "annual_report_2024.xlsx"
    report_2025 = tmp_path / "annual_report_2025.xlsx"

    _write_freedom24_report(
        report_2024,
        [
            {
                "ISIN": "X123",
                "Ticker": "X",
                "Direction": "Buy",
                "Currency": "USD",
                "Settlement date": "2024-01-10",
                "Quantity": 100,
                "Amount": 1000,
                "Price": 10,
                "Commission": "0USD",
                "Trade#": 1,
            },
            {
                "ISIN": "X123",
                "Ticker": "X",
                "Direction": "Sell",
                "Currency": "USD",
                "Settlement date": "2024-06-01",
                "Quantity": 50,
                "Amount": 600,
                "Price": 12,
                "Commission": "0USD",
                "Trade#": 2,
            },
        ],
    )
    _write_freedom24_report(
        report_2025,
        [
            {
                "ISIN": "X123",
                "Ticker": "X",
                "Direction": "Sell",
                "Currency": "USD",
                "Settlement date": "2025-03-01",
                "Quantity": 50,
                "Amount": 700,
                "Price": 14,
                "Commission": "0USD",
                "Trade#": 3,
            },
        ],
    )

    adapter = Freedom24Adapter()
    trades = load_trades_from_reports_path(adapter, tmp_path)

    closed_2024 = match_trades_and_select_tax_year(trades, 2024)
    assert len(closed_2024) == 1
    assert closed_2024[0].quantity == 50
    assert closed_2024[0].buy_amount == 500
    assert closed_2024[0].sell_amount == 600

    closed_2025 = match_trades_and_select_tax_year(trades, 2025)
    assert len(closed_2025) == 1
    assert closed_2025[0].quantity == 50
    assert closed_2025[0].buy_amount == 500
    assert closed_2025[0].sell_amount == 700
    assert closed_2025[0].buy_date.year == 2024


def test_tax_year_selection_excludes_fully_closed_prior_year_positions(tmp_path: Path) -> None:
    """If a position is fully closed in 2024, the 2025 declaration should include 0 for it."""
    report_2024 = tmp_path / "annual_report_2024.xlsx"
    _write_freedom24_report(
        report_2024,
        [
            {
                "ISIN": "Y999",
                "Ticker": "Y",
                "Direction": "Buy",
                "Currency": "USD",
                "Settlement date": "2024-01-10",
                "Quantity": 100,
                "Amount": 1000,
                "Price": 10,
                "Commission": "0USD",
                "Trade#": 1,
            },
            {
                "ISIN": "Y999",
                "Ticker": "Y",
                "Direction": "Sell",
                "Currency": "USD",
                "Settlement date": "2024-06-01",
                "Quantity": 100,
                "Amount": 1100,
                "Price": 11,
                "Commission": "0USD",
                "Trade#": 2,
            },
        ],
    )

    adapter = Freedom24Adapter()
    trades = load_trades_from_reports_path(adapter, report_2024)
    closed_2025 = match_trades_and_select_tax_year(trades, 2025)
    assert closed_2025 == []


def test_tax_year_selection_requires_buys_to_match_sells(tmp_path: Path) -> None:
    """Selling in a year without providing prior buys should fail loudly."""
    report_2025 = tmp_path / "annual_report_2025.xlsx"
    _write_freedom24_report(
        report_2025,
        [
            {
                "ISIN": "Z777",
                "Ticker": "Z",
                "Direction": "Sell",
                "Currency": "USD",
                "Settlement date": "2025-03-01",
                "Quantity": 10,
                "Amount": 100,
                "Price": 10,
                "Commission": "0USD",
                "Trade#": 1,
            },
        ],
    )

    adapter = Freedom24Adapter()
    trades = load_trades_from_reports_path(adapter, report_2025)
    with pytest.raises(Pit8cError):
        match_trades_and_select_tax_year(trades, 2025)
