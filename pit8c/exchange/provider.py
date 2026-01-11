from datetime import date
from decimal import Decimal
from typing import Protocol

from pit8c.exchange.nbp import NbpExchange


class ExchangeRatesProvider(Protocol):
    """Provides PLN exchange rates for (date, currency) pairs."""

    def prefetch(self, years: set[int], currencies: set[str]) -> None:
        """Warm up provider cache for the given years and currencies."""

    def get_rate(self, d: date, currency: str, *, use_previous_day: bool = True) -> Decimal:
        """Return an exchange rate for the given currency and date."""


class NbpExchangeRatesProvider:
    """Exchange rates provider backed by NBP archive CSV tables."""

    def __init__(self) -> None:
        self._exchange = NbpExchange()

    def prefetch(self, years: set[int], currencies: set[str]) -> None:
        """Preload NBP archive rates for required years and currencies."""

        for year in sorted(years):
            self._exchange.load_year(year, currencies)

    def get_rate(self, d: date, currency: str, *, use_previous_day: bool = True) -> Decimal:
        """Return NBP exchange rate using previous-day lookup by default."""

        return self._exchange.get_rate_for(d, currency, use_previous_day=use_previous_day)
