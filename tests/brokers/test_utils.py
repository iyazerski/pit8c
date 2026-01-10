from datetime import date, datetime

from pit8c.brokers.utils import parse_date


def test_parse_date_accepts_datetime_objects() -> None:
    """Excel readers may return native datetime values; they must be accepted as-is."""
    dt = datetime(2024, 1, 2, 3, 4, 5)
    assert parse_date(dt) == dt


def test_parse_date_accepts_date_objects() -> None:
    """Excel readers may return date values; they must be normalized to datetime."""
    assert parse_date(date(2024, 1, 2)) == datetime(2024, 1, 2)


def test_parse_date_accepts_iso_datetime_strings() -> None:
    """Timestamp-like strings should be parsed without failing."""
    assert parse_date("2024-01-02T03:04:05") == datetime(2024, 1, 2, 3, 4, 5)
