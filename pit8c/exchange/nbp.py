import csv
import io
import logging
import re
from bisect import bisect_right
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

import requests

logger = logging.getLogger(__name__)


class NbpExchange:
    """
    Downloads and caches currency rates from NBP's archive CSV for a given year.
    Provides method to get rate for a specific (date, currency) pair.
    """

    def __init__(self) -> None:
        self._rates: dict[date, dict[str, Decimal]] = {}
        self._sorted_dates: list[date] = []
        self._loaded_years: dict[int, set[str]] = {}

    def _rebuild_sorted_dates(self) -> None:
        """Rebuild the cached sorted list of available rate dates."""
        self._sorted_dates = sorted(self._rates)

    def load_year(self, year: int, currencies: set[str]) -> None:
        """
        Download the CSV from NBP archive for the given year, e.g.
        https://static.nbp.pl/dane/kursy/Archiwum/archiwum_tab_a_{year}.csv

        Parse only the currencies in the given set, e.g. {"USD", "EUR", "HUF"}.
        If a column in the header is "1USD" or "100HUF", we extract the code part
        (USD, HUF) via regex and see if it's in `currencies`.
        """
        currencies_upper = {c.upper() for c in currencies if c and c.upper() != "PLN"}
        if not currencies_upper:
            return

        already_loaded = self._loaded_years.get(year, set())
        missing_currencies = currencies_upper - already_loaded
        if not missing_currencies:
            return

        url = f"https://static.nbp.pl/dane/kursy/Archiwum/archiwum_tab_a_{year}.csv"
        logger.info("Downloading NBP archive from: %s", url)
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        reader = csv.reader(io.StringIO(response.text), delimiter=";")

        currency_indexes: dict[str, tuple[int, int]] = {}
        header_parsed = False
        added_any_date = False

        for _line_idx, row in enumerate(reader, start=1):
            if not header_parsed:
                if not row or "data" not in row[0].lower():
                    continue

                for i, val in enumerate(row):
                    match = re.match(r"^\s*(\d+)\s*([A-Za-z]+)\s*$", val)
                    if match:
                        unit = int(match.group(1))
                        currency_code = match.group(2).upper()
                        if currency_code in missing_currencies:
                            currency_indexes[currency_code] = (i, unit)

                header_parsed = True
                continue

            if not row or not row[0].isdigit():
                continue

            date_str = row[0].strip()
            if len(date_str) == 8:
                file_date = date(int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:8]))
            else:
                continue

            if file_date not in self._rates:
                self._rates[file_date] = {}
                added_any_date = True

            for curr, (idx, unit) in currency_indexes.items():
                if idx < len(row):
                    raw_val = row[idx].strip()
                    raw_val = raw_val.replace(",", ".")
                    try:
                        dec_value = Decimal(raw_val)
                    except InvalidOperation:
                        continue
                    self._rates[file_date][curr] = dec_value / Decimal(unit)

        self._loaded_years[year] = already_loaded | set(currency_indexes.keys())
        if added_any_date:
            self._rebuild_sorted_dates()

    def get_rate_for(self, d: date, currency: str, use_previous_day: bool = True) -> Decimal:
        """
        Return the exchange rate for the given currency and date.
        If `use_previous_day=True`, then we look for the last available date < d
        Otherwise, if that date is not found, raise an error or return 0.
        """

        currency = currency.upper()
        if currency == "PLN":
            return Decimal(1)

        if not self._sorted_dates:
            raise ValueError("No rates loaded. Call load_year first.")

        if use_previous_day:
            target = d - timedelta(days=1)
            idx = bisect_right(self._sorted_dates, target) - 1
            while idx >= 0:
                candidate_date = self._sorted_dates[idx]
                if currency in self._rates[candidate_date]:
                    return self._rates[candidate_date][currency]
                idx -= 1
            raise ValueError(f"No exchange rate found for {currency} prior to {d}")

        if d in self._rates:
            if currency in self._rates[d]:
                return self._rates[d][currency]
            raise ValueError(f"Currency {currency} not found for date {d}")
        raise ValueError(f"No exchange rate found for date {d}")

    def get_rates_for(self, pairs: list[tuple[date, str]]) -> list[Decimal]:
        """
        For a list of (date, currency), return a list of the corresponding exchange rates.
        By default uses `use_previous_day=True` logic. Adjust as needed.
        """
        result = []
        for d, curr in pairs:
            rate = self.get_rate_for(d, curr, use_previous_day=True)
            result.append(rate)
        return result
