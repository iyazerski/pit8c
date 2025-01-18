from datetime import datetime
from decimal import Decimal

import pytest

from pit38.models import ClosedPosition, DirectionEnum, Trade
from pit38.trades_finder import match_trades_fifo


@pytest.mark.parametrize(
    "trades_input, expected_len, expected_first_quantity",
    [
        (
            [
                Trade(
                    ISIN="TEST123",
                    TradeNum=123,
                    Ticker="TST",
                    Currency="USD",
                    Direction=DirectionEnum.buy,
                    Date=datetime(2024, 1, 1),
                    Quantity=Decimal("10"),
                    Amount=Decimal("1000"),
                    CommissionValue=Decimal("10"),
                ),
                Trade(
                    ISIN="TEST123",
                    TradeNum=124,
                    Ticker="TST",
                    Currency="USD",
                    Direction=DirectionEnum.sell,
                    Date=datetime(2024, 1, 2),
                    Quantity=Decimal("10"),
                    Amount=Decimal("1200"),
                    CommissionValue=Decimal("5"),
                ),
            ],
            1,
            Decimal("10"),
        ),
        (
            [
                Trade(
                    ISIN="XYZ999",
                    TradeNum=123,
                    Ticker="XYZ",
                    Currency="USD",
                    Direction=DirectionEnum.buy,
                    Date=datetime(2024, 1, 10),
                    Quantity=Decimal("5"),
                    Amount=Decimal("500"),
                    CommissionValue=Decimal("5"),
                ),
                Trade(
                    ISIN="XYZ999",
                    TradeNum=124,
                    Ticker="XYZ",
                    Currency="USD",
                    Direction=DirectionEnum.buy,
                    Date=datetime(2024, 1, 15),
                    Quantity=Decimal("5"),
                    Amount=Decimal("600"),
                    CommissionValue=Decimal("6"),
                ),
                Trade(
                    ISIN="XYZ999",
                    TradeNum=125,
                    Ticker="XYZ",
                    Currency="USD",
                    Direction=DirectionEnum.sell,
                    Date=datetime(2024, 2, 1),
                    Quantity=Decimal("8"),
                    Amount=Decimal("1000"),
                    CommissionValue=Decimal("10"),
                ),
            ],
            2,
            Decimal("5"),
        ),
    ],
)
def test_fifo(trades_input, expected_len, expected_first_quantity):
    closed_positions = match_trades_fifo(trades_input)
    assert len(closed_positions) == expected_len
    assert isinstance(closed_positions[0], ClosedPosition)
    assert closed_positions[0].Quantity == expected_first_quantity
