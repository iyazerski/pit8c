from datetime import datetime
from decimal import Decimal

from pit8c.exchange.rates import fill_exchange_rates
from pit8c.models import ClosedPosition


class _DummyProvider:
    def __init__(self) -> None:
        """Create a provider stub that records prefetch calls and serves fixed rates."""

        self.prefetch_calls: list[tuple[set[int], set[str]]] = []

    def prefetch(self, years: set[int], currencies: set[str]) -> None:
        """Record requested years/currencies for later assertions."""

        self.prefetch_calls.append((set(years), set(currencies)))

    def get_rate(self, _d: object, currency: str, *, use_previous_day: bool = True) -> Decimal:
        """Return deterministic rates for requested currencies (previous-day flag ignored)."""

        _ = use_previous_day
        return {"USD": Decimal("4.00"), "EUR": Decimal("4.50"), "PLN": Decimal(1)}[currency.upper()]


def test_fill_exchange_rates_includes_commission_currencies() -> None:
    """Commission currencies are loaded and their rates are filled separately from the trade currency."""
    dummy = _DummyProvider()

    cp = ClosedPosition(
        isin="TEST123",
        ticker="TST",
        currency="USD",
        buy_date=datetime(2024, 1, 2),
        quantity=Decimal(1),
        buy_amount=Decimal(100),
        sell_date=datetime(2024, 2, 1),
        sell_amount=Decimal(120),
        buy_commission=Decimal(1),
        sell_commission=Decimal(2),
        buy_commission_currency="EUR",
        sell_commission_currency="USD",
    )

    fill_exchange_rates([cp], provider=dummy)

    years, currencies = dummy.prefetch_calls[0]
    assert 2024 in years
    assert {"USD", "EUR"} <= currencies

    assert cp.buy_exchange_rate == Decimal("4.00")
    assert cp.sell_exchange_rate == Decimal("4.00")
    assert cp.buy_commission_exchange_rate == Decimal("4.50")
    assert cp.sell_commission_exchange_rate == Decimal("4.00")
