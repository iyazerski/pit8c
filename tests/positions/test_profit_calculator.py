from datetime import datetime
from decimal import Decimal

from pit8c.models import ClosedPosition
from pit8c.positions.profit_calculator import calculate_profit


def test_profit_calculator_converts_amounts_and_commissions_in_pln() -> None:
    """Income and costs are computed in PLN using the provided exchange rates."""
    cp = ClosedPosition(
        isin="TEST123",
        ticker="TST",
        currency="USD",
        buy_date=datetime(2024, 1, 1),
        quantity=Decimal(1),
        buy_amount=Decimal(100),
        sell_date=datetime(2024, 2, 1),
        sell_amount=Decimal(120),
        buy_commission=Decimal(1),
        sell_commission=Decimal(2),
        buy_commission_currency="USD",
        sell_commission_currency="USD",
        buy_exchange_rate=Decimal("4.00"),
        sell_exchange_rate=Decimal("4.10"),
        buy_commission_exchange_rate=Decimal("4.00"),
        sell_commission_exchange_rate=Decimal("4.10"),
    )

    profit_positions, loss_positions = calculate_profit([cp])
    assert len(loss_positions) == 0
    assert len(profit_positions) == 1

    assert cp.income_pln == Decimal("492.00")
    assert cp.costs_pln == Decimal("412.20")


def test_profit_calculator_supports_commissions_in_different_currency() -> None:
    """Commissions may be charged in a currency different from the trade currency."""
    cp = ClosedPosition(
        isin="TEST123",
        ticker="TST",
        currency="USD",
        buy_date=datetime(2024, 1, 1),
        quantity=Decimal(1),
        buy_amount=Decimal(100),
        sell_date=datetime(2024, 2, 1),
        sell_amount=Decimal(120),
        buy_commission=Decimal(1),
        sell_commission=Decimal(2),
        buy_commission_currency="EUR",
        sell_commission_currency="USD",
        buy_exchange_rate=Decimal("4.00"),
        sell_exchange_rate=Decimal("4.10"),
        buy_commission_exchange_rate=Decimal("4.50"),
        sell_commission_exchange_rate=Decimal("4.10"),
    )

    calculate_profit([cp])

    assert cp.income_pln == Decimal("492.00")
    assert cp.costs_pln == Decimal("412.70")
