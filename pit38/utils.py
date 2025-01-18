import re
from datetime import datetime
from decimal import Decimal


def parse_date(date_str: str) -> datetime | None:
    """
    Parse a string in YYYY-MM-DD format into a datetime.
    If parsing fails, returns None or raises ValueError.
    """
    date_str = date_str.strip()
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def parse_commission(commission_str: str) -> tuple[Decimal, str]:
    """
    Parse commission string like '2.28EUR', '2.24USD', etc. into (value, currency).
    If none or empty, returns (Decimal("0"), "").
    """
    default_commission = Decimal("0"), ""

    commission_str = commission_str.strip()
    if not commission_str:
        return default_commission

    match = re.match(r"^([0-9]+(\.[0-9]+)?)([A-Za-z]+)$", commission_str)
    if match:
        value_str = match.group(1)
        currency_str = match.group(3)
        return Decimal(value_str), currency_str.upper()

    return default_commission
