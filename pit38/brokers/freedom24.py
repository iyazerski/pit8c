from datetime import datetime
from typing import Any

from pit38.brokers.base import BrokerAdapter
from pit38.utils import parse_commission, parse_date


class Freedom24Adapter(BrokerAdapter):
    """
    Adapter for Freedom24 annual reports.
    Expects specific column names (like 'ISIN', 'Ticker', 'Trade#', 'Direction', etc.).
    """

    def parse_trades(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Parse the raw data rows from Freedom24 into standardized trades.
        """
        parsed = []
        for row in raw_data:
            isin = (row.get("ISIN") or "").strip()
            direction = (row.get("Direction") or "").strip().lower()  # "buy" or "sell" or ...
            ticker = (row.get("Ticker") or "").strip()
            currency = (row.get("Currency") or "").strip()
            quantity = float(row.get("Quantity") or 0.0)
            amount = float(row.get("Amount") or 0.0)

            date_str = (row.get("Settlement date") or "").strip()
            trade_date: datetime | None = parse_date(date_str)  # from utils

            price = float(row.get("Price") or 0.0)

            # Commission can look like '2.28EUR', '2.10USD', or be empty.
            commission_str = str(row.get("Commission") or "")
            comm_value, comm_curr = parse_commission(commission_str)

            # Trade number
            trade_num = 0
            if "Trade#" in row:
                try:
                    trade_num = int(row["Trade#"])
                except ValueError:
                    trade_num = 0

            parsed.append(
                {
                    "ISIN": isin,
                    "Ticker": ticker,
                    "Direction": direction,
                    "Quantity": quantity,
                    "Price": price,
                    "Currency": currency,
                    "Amount": amount,
                    "Date": trade_date,
                    "CommissionValue": comm_value,
                    "CommissionCurrency": comm_curr,
                    "TradeNum": trade_num,
                }
            )

        return parsed
