from datetime import datetime
from typing import Any

import openpyxl
from openpyxl import Workbook


def read_trades_from_xlsx(filename: str, sheet_name: str | None = None) -> list[dict[str, Any]]:
    """
    Reads an XLSX file (entire sheet) into a list of dictionaries (raw data).
    The first row is assumed to be the header.
    """
    wb = openpyxl.load_workbook(filename, data_only=True)
    if sheet_name is None:
        sheet = wb.active
    else:
        sheet = wb[sheet_name]

    rows = list(sheet.rows)
    if not rows:
        return []

    headers = [cell.value if cell.value else "" for cell in rows[0]]
    data_rows = rows[1:]

    out_data = []
    for row in data_rows:
        row_dict = {}
        for col_idx, cell in enumerate(row):
            header = headers[col_idx].strip() if col_idx < len(headers) else f"Unlabeled_{col_idx}"
            row_dict[header] = cell.value
        out_data.append(row_dict)

    return out_data


def write_trades_to_xlsx(closed_positions: list[dict[str, Any]], out_filename: str) -> None:
    """
    Writes the matched buy-sell trades to a new XLSX file.
    Columns required:
      ISIN, Ticker, Currency, BuyAmount, BuyDate, SellAmount, SellDate, TotalCommission
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Closed Positions"

    headers = [
        "ISIN",
        "Ticker",
        "Currency",
        "BuyAmount",
        "BuyDate",
        "SellAmount",
        "SellDate",
        "TotalCommission",
    ]
    ws.append(headers)

    # sort by ISIN, SellDate for clarity
    sorted_positions = sorted(closed_positions, key=lambda x: (x["ISIN"], x["SellDate"]))

    for pos in sorted_positions:
        buy_date_str = (
            pos["BuyDate"].strftime("%Y-%m-%d") if isinstance(pos["BuyDate"], datetime) else str(pos["BuyDate"])
        )
        sell_date_str = (
            pos["SellDate"].strftime("%Y-%m-%d") if isinstance(pos["SellDate"], datetime) else str(pos["SellDate"])
        )

        row = [
            pos.get("ISIN", ""),
            pos.get("Ticker", ""),
            pos.get("Currency", ""),
            round(pos.get("BuyAmount", 0.0), 4),
            buy_date_str,
            round(pos.get("SellAmount", 0.0), 4),
            sell_date_str,
            round(pos.get("TotalCommission", 0.0), 4),
        ]
        ws.append(row)

    wb.save(out_filename)
