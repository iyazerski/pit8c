from datetime import datetime
from decimal import Decimal

import pytest
from pit8c.brokers.freedom24 import Freedom24Adapter
from pit8c.models import DirectionEnum


@pytest.mark.parametrize(
    (
        "row_input",
        "expected_isin",
        "expected_dir",
        "expected_date",
        "expected_quantity",
        "expected_amount",
        "expected_comm_value",
        "expected_trade_num",
    ),
    [
        (
            {
                "ISIN": "TEST123",
                "Ticker": "TST",
                "Direction": "Buy",
                "Currency": "USD",
                "Settlement date": "2024-01-01",
                "Quantity": 10,
                "Amount": 1000,
                "Price": 100,
                "Commission": "2.50USD",
                "Trade#": 1234,
            },
            "TEST123",
            DirectionEnum.buy,
            datetime(2024, 1, 1),
            Decimal(10),
            Decimal(1000),
            Decimal("2.50"),
            1234,
        ),
        (
            {
                "ISIN": "ABC999",
                "Ticker": "ABC",
                "Direction": "Sell",
                "Currency": "EUR",
                "Settlement date": "2024-03-15",
                "Quantity": 3,
                "Amount": 450,
                "Price": 150,
                "Commission": "1.00EUR",
                "Trade#": 999,
            },
            "ABC999",
            DirectionEnum.sell,
            datetime(2024, 3, 15),
            Decimal(3),
            Decimal(450),
            Decimal("1.00"),
            999,
        ),
    ],
)
def test_freedom24_adapter_minimal(
    row_input: dict[str, object],
    expected_isin: str,
    expected_dir: DirectionEnum,
    expected_date: datetime,
    expected_quantity: Decimal,
    expected_amount: Decimal,
    expected_comm_value: Decimal,
    expected_trade_num: int,
) -> None:
    """
    Parametric test to check that Freedom24Adapter correctly parses
    different sets of raw row data into Trade models.
    """
    adapter = Freedom24Adapter()
    raw_data = [row_input]
    trades = adapter.parse_trades(raw_data)

    assert len(trades) == 1, "Adapter should return exactly one Trade for one raw row"
    trade = trades[0]

    assert trade.isin == expected_isin
    assert trade.direction == expected_dir
    assert trade.date == expected_date
    assert trade.quantity == expected_quantity
    assert trade.amount == expected_amount
    assert trade.commission_value == expected_comm_value
    assert trade.trade_num == expected_trade_num


def test_freedom24_adapter_prefers_trade_date_over_settlement_date() -> None:
    """PIT-8C calculations should use transaction date rather than settlement date when available."""
    adapter = Freedom24Adapter()
    trades = adapter.parse_trades(
        [
            {
                "ISIN": "TEST123",
                "Ticker": "TST",
                "Direction": "Buy",
                "Currency": "USD",
                "Trade date": "2024-01-01",
                "Settlement date": "2024-01-03",
                "Quantity": 1,
                "Amount": 100,
                "Price": 100,
                "Commission": "0USD",
                "Trade#": 1,
            }
        ]
    )

    assert len(trades) == 1
    assert trades[0].date == datetime(2024, 1, 1)


def test_freedom24_adapter_parses_fee_column_as_commission() -> None:
    """Some Freedom24 exports use 'Fee' instead of 'Commission'."""
    adapter = Freedom24Adapter()
    trades = adapter.parse_trades(
        [
            {
                "ISIN": "TEST123",
                "Ticker": "TST",
                "Direction": "Sell",
                "Currency": "USD",
                "Settlement date": "2024-01-03",
                "Quantity": 1,
                "Amount": 100,
                "Price": 100,
                "Fee": "6.00USD",
                "Trade#": 1,
            }
        ]
    )

    assert len(trades) == 1
    assert trades[0].commission_value == Decimal("6.00")
    assert trades[0].commission_currency == "USD"
