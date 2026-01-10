import re
from datetime import date, datetime
from decimal import Decimal


def parse_date(value: object) -> datetime | None:
    """
    Parse broker-provided dates into a datetime.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)

    if not isinstance(value, str):
        value = str(value)

    date_str = value.strip()
    if not date_str:
        return None

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def parse_commission(commission_str: str) -> tuple[Decimal, str]:
    """
    Parse commission string like '2.28EUR', '2.24USD', etc. into (value, currency).
    If none or empty, returns (Decimal("0"), "").
    """
    default_commission = Decimal(0), ""

    commission_str = commission_str.strip()
    if not commission_str:
        return default_commission

    match = re.match(r"^([0-9]+(\.[0-9]+)?)([A-Za-z]+)$", commission_str)
    if match:
        value_str = match.group(1)
        currency_str = match.group(3)
        return Decimal(value_str), currency_str.upper()

    return default_commission
