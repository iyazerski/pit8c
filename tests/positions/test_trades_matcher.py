from datetime import datetime
from decimal import Decimal

import pytest
from pit8c.exceptions import Pit8cError
from pit8c.models import ClosedPosition, DirectionEnum, Trade
from pit8c.positions.trades_matcher import match_trades_fifo


@pytest.mark.parametrize(
    ("trades_input", "expected_len", "expected_first_quantity"),
    [
        (
            [
                Trade(
                    isin="TEST123",
                    trade_num=123,
                    ticker="TST",
                    currency="USD",
                    direction=DirectionEnum.buy,
                    date=datetime(2024, 1, 1),
                    quantity=Decimal(10),
                    amount=Decimal(1000),
                    commission_value=Decimal(10),
                ),
                Trade(
                    isin="TEST123",
                    trade_num=124,
                    ticker="TST",
                    currency="USD",
                    direction=DirectionEnum.sell,
                    date=datetime(2024, 1, 2),
                    quantity=Decimal(10),
                    amount=Decimal(1200),
                    commission_value=Decimal(5),
                ),
            ],
            1,
            Decimal(10),
        ),
        (
            [
                Trade(
                    isin="XYZ999",
                    trade_num=123,
                    ticker="XYZ",
                    currency="USD",
                    direction=DirectionEnum.buy,
                    date=datetime(2024, 1, 10),
                    quantity=Decimal(5),
                    amount=Decimal(500),
                    commission_value=Decimal(5),
                ),
                Trade(
                    isin="XYZ999",
                    trade_num=124,
                    ticker="XYZ",
                    currency="USD",
                    direction=DirectionEnum.buy,
                    date=datetime(2024, 1, 15),
                    quantity=Decimal(5),
                    amount=Decimal(600),
                    commission_value=Decimal(6),
                ),
                Trade(
                    isin="XYZ999",
                    trade_num=125,
                    ticker="XYZ",
                    currency="USD",
                    direction=DirectionEnum.sell,
                    date=datetime(2024, 2, 1),
                    quantity=Decimal(8),
                    amount=Decimal(1000),
                    commission_value=Decimal(10),
                ),
            ],
            2,
            Decimal(5),
        ),
    ],
)
def test_fifo(trades_input: list[Trade], expected_len: int, expected_first_quantity: Decimal) -> None:
    closed_positions = match_trades_fifo(trades_input)
    assert len(closed_positions) == expected_len
    assert isinstance(closed_positions[0], ClosedPosition)
    assert closed_positions[0].quantity == expected_first_quantity


def test_fifo_multiple_partial_closures_preserve_buy_amounts_and_commissions() -> None:
    trades = [
        Trade(
            isin="TEST123",
            trade_num=1,
            ticker="TST",
            currency="USD",
            direction=DirectionEnum.buy,
            date=datetime(2024, 1, 1),
            quantity=Decimal(10),
            amount=Decimal(1000),
            commission_value=Decimal(10),
        ),
        Trade(
            isin="TEST123",
            trade_num=2,
            ticker="TST",
            currency="USD",
            direction=DirectionEnum.sell,
            date=datetime(2024, 1, 2),
            quantity=Decimal(4),
            amount=Decimal(600),
            commission_value=Decimal(4),
        ),
        Trade(
            isin="TEST123",
            trade_num=3,
            ticker="TST",
            currency="USD",
            direction=DirectionEnum.sell,
            date=datetime(2024, 1, 3),
            quantity=Decimal(6),
            amount=Decimal(900),
            commission_value=Decimal(6),
        ),
    ]

    closed_positions = match_trades_fifo(trades)
    assert [cp.quantity for cp in closed_positions] == [Decimal(4), Decimal(6)]
    assert [cp.buy_amount for cp in closed_positions] == [Decimal(400), Decimal(600)]
    assert [cp.buy_commission for cp in closed_positions] == [Decimal(4), Decimal(6)]
    assert [cp.sell_amount for cp in closed_positions] == [Decimal(600), Decimal(900)]
    assert [cp.sell_commission for cp in closed_positions] == [Decimal(4), Decimal(6)]

    assert sum((cp.buy_amount for cp in closed_positions), Decimal(0)) == Decimal(1000)
    assert sum((cp.buy_commission for cp in closed_positions), Decimal(0)) == Decimal(10)


def test_fifo_rejects_sell_without_buys() -> None:
    trades = [
        Trade(
            isin="TEST123",
            trade_num=1,
            ticker="TST",
            currency="USD",
            direction=DirectionEnum.sell,
            date=datetime(2024, 1, 2),
            quantity=Decimal(1),
            amount=Decimal(100),
            commission_value=Decimal(1),
        ),
    ]

    with pytest.raises(Pit8cError):
        match_trades_fifo(trades)
