from decimal import Decimal


def serialize_decimal(value: Decimal) -> str:
    if value.is_zero() or value.is_nan():
        return "0.0"
    return str(value)
