from typing import Any, Protocol


class BrokerAdapter(Protocol):
    """
    Base interface for reading & parsing raw broker XLSX data into a standardized format
    suitable for FIFO matching.
    """

    def parse_trades(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Parse raw data (after reading from XLSX) into a standardized list of trades.
        Each item must have keys like:
          - ISIN
          - Ticker
          - Direction ("buy" or "sell")
          - Quantity (float)
          - Price (float)
          - Currency (str)
          - Amount (float)
          - Date (datetime)
          - CommissionValue (float)
          - CommissionCurrency (str)
          - TradeNum (int)
        """
        ...
