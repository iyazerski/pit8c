from datetime import datetime
from decimal import Decimal

from pit8c import DirectionEnum, Pit8c, Trade
from pit8c.exchange.provider import ExchangeRatesProvider


class _DummyProvider:
    def prefetch(self, years: set[int], currencies: set[str]) -> None:
        """Ignore prefetch requests and serve deterministic rates."""

        _ = years
        _ = currencies

    def get_rate(self, _d: object, _currency: str, *, use_previous_day: bool = True) -> Decimal:
        """Return a constant USD rate for tests (previous-day flag ignored)."""

        _ = use_previous_day
        return Decimal("4.00")


def test_process_trades_computes_totals_without_writing() -> None:
    provider: ExchangeRatesProvider = _DummyProvider()
    pit8c = Pit8c(exchange_provider=provider, write_pdf=False, write_xlsx=False)

    trades = [
        Trade(
            isin="TEST123",
            ticker="TST",
            currency="USD",
            direction=DirectionEnum.buy,
            date=datetime(2024, 1, 1),
            quantity=Decimal(1),
            amount=Decimal(100),
            commission_value=Decimal(0),
        ),
        Trade(
            isin="TEST123",
            ticker="TST",
            currency="USD",
            direction=DirectionEnum.sell,
            date=datetime(2024, 2, 1),
            quantity=Decimal(1),
            amount=Decimal(120),
            commission_value=Decimal(0),
        ),
    ]

    result = pit8c.process_trades(trades, tax_year=2024)
    assert result.tax_year == 2024
    assert len(result.closed_positions) == 1
    assert result.totals.income_pln == Decimal("480.00")
    assert result.totals.costs_pln == Decimal("400.00")
    assert result.totals.profit_pln == Decimal("80.00")
    assert result.artifacts.pit8c_pdf_path is None
    assert result.artifacts.closed_positions_xlsx_path is None
    assert result.artifacts.pit8c_text is not None
