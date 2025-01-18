from datetime import datetime
from typing import Any

import openpyxl
from openpyxl import Workbook

from pit38.models import ClosedPosition


def read_trades_from_xlsx(filename: str, sheet_name: str | None = None) -> list[dict[str, Any]]:
    """
    Reads an XLSX file (entire sheet) into a list of dictionaries (raw data).
    The first row is assumed to be the header.
    """
    wb = openpyxl.load_workbook(filename, data_only=True)
    sheet = wb[sheet_name] if sheet_name else wb.active

    rows = list(sheet.rows)
    if not rows:
        return []

    headers = [cell.value if cell.value else "" for cell in rows[0]]
    raw_data = []
    for row in rows[1:]:
        row_dict = {}
        for col_idx, cell in enumerate(row):
            if col_idx < len(headers):
                header = headers[col_idx].strip()
                row_dict[header] = cell.value
        raw_data.append(row_dict)
    return raw_data


def write_trades_to_xlsx(closed_positions: list[ClosedPosition], out_filename: str) -> None:
    """
    Write the closed positions to XLSX.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Closed Positions"

    headers = [
        "ISIN",
        "Ticker",
        "Currency",
        "Quantity",
        "BuyAmount",
        "BuyDate",
        "SellAmount",
        "SellDate",
        "TotalCommission",
    ]
    ws.append(headers)

    # Sort for readability
    sorted_positions = sorted(closed_positions, key=lambda cp: (cp.ISIN, cp.SellDate))

    for pos in sorted_positions:
        # Convert date -> YYYY-MM-DD
        buy_date_str = pos.BuyDate.strftime("%Y-%m-%d") if isinstance(pos.BuyDate, datetime) else str(pos.BuyDate)
        sell_date_str = pos.SellDate.strftime("%Y-%m-%d") if isinstance(pos.SellDate, datetime) else str(pos.SellDate)

        row = [
            pos.ISIN,
            pos.Ticker,
            pos.Currency,
            str(pos.Quantity),
            str(pos.BuyAmount),
            buy_date_str,
            str(pos.SellAmount),
            sell_date_str,
            str(pos.TotalCommission),
        ]
        ws.append(row)

    wb.save(out_filename)
