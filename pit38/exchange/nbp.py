import csv
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

import requests


class NbpExchange:
    """
    Downloads and caches currency rates from NBP's archive CSV for a given year.
    Provides method to get rate for a specific (date, currency) pair.
    """

    def __init__(self):
        self._rates: dict[date, dict[str, Decimal]] = {}

    def load_year(self, year: int, currencies: set[str]) -> None:
        """
        Download the CSV from NBP archive for the given year, e.g.
        https://static.nbp.pl/dane/kursy/Archiwum/archiwum_tab_a_{year}.csv

        Parse only the currencies in the given set, e.g. {"USD", "EUR", "HUF"}.
        If a column in the header is "1USD" or "100HUF", we extract the code part
        (USD, HUF) via regex and see if it's in `currencies`.
        """
        url = f"https://static.nbp.pl/dane/kursy/Archiwum/archiwum_tab_a_{year}.csv"
        print(f"Downloading NBP archive from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        content = response.text.splitlines()
        reader = csv.reader(content, delimiter=";")

        currency_indexes = {}
        header_parsed = False

        for line_idx, row in enumerate(reader, start=1):
            if not header_parsed:
                if not row or "data" not in row[0].lower():
                    continue

                for i, val in enumerate(row):
                    match = re.match(r"^(\d+)([A-Za-z]+)$", val.strip())
                    if match:
                        currency_code = match.group(2).upper()
                        if currency_code in currencies:
                            currency_indexes[currency_code] = i

                header_parsed = True
                continue

            if not row or not row[0].isdigit():
                continue

            date_str = row[0].strip()
            if len(date_str) == 8:
                file_date = datetime.strptime(date_str, "%Y%m%d").date()
            else:
                continue

            if file_date not in self._rates:
                self._rates[file_date] = {}

            for curr, idx in currency_indexes.items():
                if idx < len(row):
                    raw_val = row[idx].strip()
                    raw_val = raw_val.replace(",", ".")
                    try:
                        dec_value = Decimal(raw_val)
                    except InvalidOperation:
                        dec_value = Decimal("0")
                    self._rates[file_date][curr] = dec_value

    def get_rate_for(self, d: date, currency: str, use_previous_day: bool = True) -> Decimal:
        """
        Return the exchange rate for the given currency and date.
        If `use_previous_day=True`, then we look for the last available date < d
        Otherwise, if that date is not found, raise an error or return 0.
        """

        all_dates = sorted(self._rates.keys())
        if not all_dates:
            raise ValueError("No rates loaded. Call load_year first.")

        if use_previous_day:
            check_date = d - timedelta(days=1)
            while check_date >= all_dates[0]:
                if check_date in self._rates:
                    if currency in self._rates[check_date]:
                        return self._rates[check_date][currency]
                    else:
                        raise ValueError(f"Currency {currency} not found for date {check_date}")
                check_date = check_date - timedelta(days=1)

            raise ValueError(f"No exchange rate found for {currency} prior to {d}")

        else:
            if d in self._rates:
                if currency in self._rates[d]:
                    return self._rates[d][currency]
                else:
                    raise ValueError(f"Currency {currency} not found for date {d}")
            else:
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
