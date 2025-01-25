from enum import Enum
from typing import Any, Protocol

from pit38.models import Trade


class BrokerAdapter(Protocol):
    """
    Base interface for reading & parsing raw broker XLSX data into a standardized format
    suitable for FIFO matching.
    """

    def parse_trades(self, raw_data: list[dict[str, Any]]) -> list[Trade]:
        """
        Parse raw data (after reading from XLSX) into a standardized list of trades.
        """
        ...


class SupportedBroker(str, Enum):
    freedom24 = "freedom24"
