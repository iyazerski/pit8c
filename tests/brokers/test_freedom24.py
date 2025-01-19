from datetime import datetime
from decimal import Decimal

import pytest

from pit38.brokers.freedom24 import Freedom24Adapter
from pit38.models import DirectionEnum


@pytest.mark.parametrize(
    "row_input, expected_isin, expected_dir, expected_date, expected_quantity, expected_amount, expected_comm_value, expected_trade_num",
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
            Decimal("10"),
            Decimal("1000"),
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
            Decimal("3"),
            Decimal("450"),
            Decimal("1.00"),
            999,
        ),
    ],
)
def test_freedom24_adapter_minimal(
    row_input,
    expected_isin,
    expected_dir,
    expected_date,
    expected_quantity,
    expected_amount,
    expected_comm_value,
    expected_trade_num,
):
    """
    Parametric test to check that Freedom24Adapter correctly parses
    different sets of raw row data into Trade models.
    """
    adapter = Freedom24Adapter()
    raw_data = [row_input]
    trades = adapter.parse_trades(raw_data)

    assert len(trades) == 1, "Adapter should return exactly one Trade for one raw row"
    trade = trades[0]

    assert trade.ISIN == expected_isin
    assert trade.Direction == expected_dir
    assert trade.Date == expected_date
    assert trade.Quantity == expected_quantity
    assert trade.Amount == expected_amount
    assert trade.CommissionValue == expected_comm_value
    assert trade.TradeNum == expected_trade_num
