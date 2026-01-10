from collections.abc import Callable
from datetime import date
from decimal import Decimal

import pytest
from pit8c.exchange.nbp import NbpExchange


class _DummyResponse:
    def __init__(self, text: str) -> None:
        """Create a response-like object with a fixed text body."""
        self.text = text

    def raise_for_status(self) -> None:
        """Mimic requests.Response.raise_for_status for successful responses."""
        return None


def _make_get(text: str) -> Callable[[str, int], _DummyResponse]:
    """Create a stub replacement for requests.get that returns a fixed response body."""

    def _get(_url: str, timeout: int) -> _DummyResponse:
        """Return a dummy response for any request URL."""
        _ = timeout
        return _DummyResponse(text)

    return _get


def test_nbp_parses_unit_multipliers_and_normalizes_rates(monkeypatch: pytest.MonkeyPatch) -> None:
    """NBP CSV headers like '100HUF' are normalized to per-1-unit exchange rates."""
    csv_text = "\n".join(
        [
            "data;1USD;100HUF",
            "20240102;4,10;101,00",
        ]
    )
    monkeypatch.setattr("requests.get", _make_get(csv_text))

    exchange = NbpExchange()
    exchange.load_year(2024, {"USD", "HUF"})

    assert exchange.get_rate_for(date(2024, 1, 3), "USD", use_previous_day=True) == Decimal("4.10")
    assert exchange.get_rate_for(date(2024, 1, 3), "HUF", use_previous_day=True) == Decimal("1.01")
    assert exchange.get_rate_for(date(2024, 1, 3), "PLN", use_previous_day=True) == Decimal(1)


def test_nbp_previous_day_lookup_can_cross_year_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Previous-day lookup may require rates from the prior calendar year."""
    csv_2023 = "\n".join(
        [
            "data;1USD",
            "20231229;4,00",
        ]
    )
    csv_2024 = "\n".join(
        [
            "data;1USD",
            "20240102;4,10",
        ]
    )

    def _get(url: str, timeout: int) -> _DummyResponse:
        """Return year-specific CSV content based on the requested URL."""
        _ = timeout
        return _DummyResponse(csv_2023 if "archiwum_tab_a_2023.csv" in url else csv_2024)

    monkeypatch.setattr("requests.get", _get)

    exchange = NbpExchange()
    exchange.load_year(2023, {"USD"})
    exchange.load_year(2024, {"USD"})

    assert exchange.get_rate_for(date(2024, 1, 1), "USD", use_previous_day=True) == Decimal("4.00")


def test_nbp_skips_invalid_values_and_keeps_searching(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid/missing numeric cells are skipped and earlier dates are used if needed."""
    csv_text = "\n".join(
        [
            "data;100HUF",
            "20240101;100,00",
            "20240102;",
        ]
    )
    monkeypatch.setattr("requests.get", _make_get(csv_text))

    exchange = NbpExchange()
    exchange.load_year(2024, {"HUF"})

    # 2024-01-03 previous day is 2024-01-02 (missing), so it should fall back to 2024-01-01.
    assert exchange.get_rate_for(date(2024, 1, 3), "HUF", use_previous_day=True) == Decimal("1.00")
