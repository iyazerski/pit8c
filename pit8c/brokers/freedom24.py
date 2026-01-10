from decimal import Decimal
from typing import Any

from pit8c.brokers.base import BrokerAdapter
from pit8c.brokers.utils import parse_commission, parse_date
from pit8c.models import DirectionEnum, Trade


class Freedom24Adapter(BrokerAdapter):
    """
    Adapter for Freedom24 annual reports.
    It parses the raw XLSX data into a list of Trade objects.
    """

    def parse_trades(self, raw_data: list[dict[str, Any]]) -> list[Trade]:
        """
        Convert each row (a dict) from Freedom24's XLSX format
        into our unified Trade model.
        """
        trades: list[Trade] = []

        for row in raw_data:
            # Extract raw fields
            isin_raw = (row.get("ISIN") or "").strip()
            ticker_raw = (row.get("Ticker") or "").strip()
            direction_label = (row.get("Direction") or "").lower().strip()  # "buy"/"sell"
            if "buy" in direction_label:
                direction = DirectionEnum.buy
            elif "sell" in direction_label:
                direction = DirectionEnum.sell
            else:
                # Be tolerant to unrelated XLSX files in a directory input (e.g. tool output XLSX).
                continue

            currency_raw = (row.get("Currency") or "").strip()

            # For PIT-8C the relevant date is the transaction (trade) date; settlement date can be T+2.
            dt = parse_date(row.get("Trade date") or row.get("Settlement date"))  # returns datetime or None

            # Quantity, Amount, Price, etc. might be float or None
            qty_val = row.get("Quantity", 0)
            amt_val = row.get("Amount", 0)
            price_val = row.get("Price", 0)

            # Commission (e.g. "2.28EUR" -> (Decimal('2.28'), 'EUR'))
            comm_str = str(row.get("Commission") or row.get("Fee") or "")
            comm_value, comm_curr = parse_commission(comm_str)

            # Trade number
            trade_num = 0
            if "Trade#" in row:
                try:
                    trade_num = int(row["Trade#"])
                except (ValueError, TypeError):
                    trade_num = 0

            if dt is None:
                continue

            trade_obj = Trade(
                isin=isin_raw,
                ticker=ticker_raw,
                currency=currency_raw,
                direction=direction,
                date=dt,
                quantity=Decimal(str(qty_val)),
                amount=Decimal(str(amt_val)),
                commission_value=comm_value,
                commission_currency=comm_curr,
                price=Decimal(str(price_val)) if price_val else None,
                trade_num=trade_num,
            )

            trades.append(trade_obj)

        return trades
