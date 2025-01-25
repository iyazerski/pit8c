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
    Standardized trade model for input from broker adapters.
    """

    isin: str
    ticker: str
    currency: str
    direction: DirectionEnum
    date: datetime
    quantity: Decimal
    amount: Decimal
    commission_value: Decimal
    commission_currency: str = Field(default="")
    price: Optional[Decimal] = Field(default=None)
    trade_num: int = Field(default=0)


class ClosedPosition(BaseModel):
    """
    Represents a closed position after matching a buy-lot with a sell-lot.
    """

    isin: str
    ticker: str
    currency: str

    buy_date: datetime
    quantity: Decimal
    buy_amount: Decimal

    sell_date: datetime
    sell_amount: Decimal

    buy_commission: Decimal = Field(default=Decimal("0"))
    sell_commission: Decimal = Field(default=Decimal("0"))

    buy_exchange_rate: Decimal = Field(default=Decimal("0"))
    sell_exchange_rate: Decimal = Field(default=Decimal("0"))

    profit: Decimal = Field(default=Decimal("0"))

    # fields required for PIT-8C and PIT-38
    income_pln: Decimal = Field(default=Decimal("0"))
    costs_pln: Decimal = Field(default=Decimal("0"))
