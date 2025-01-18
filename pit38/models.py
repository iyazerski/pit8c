from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DirectionEnum(str, Enum):
    buy = "buy"
    sell = "sell"


class Trade(BaseModel):
    """
    A standardized representation of a single trade.
    All brokers' adapters must convert raw XLSX rows into this model.
    """

    ISIN: str
    Ticker: str
    Currency: str
    TradeNum: int
    Direction: DirectionEnum
    Date: datetime
    Quantity: Decimal
    Amount: Decimal
    CommissionValue: Decimal
    CommissionCurrency: str = Field(default="")
    Price: Optional[Decimal] = Field(default=None)


class ClosedPosition(BaseModel):
    """
    Represents a closed position after matching a buy-lot with a sell-lot.
    """

    ISIN: str
    Ticker: str
    Currency: str
    BuyDate: datetime
    Quantity: Decimal
    BuyAmount: Decimal
    SellDate: datetime
    SellAmount: Decimal
    TotalCommission: Decimal
