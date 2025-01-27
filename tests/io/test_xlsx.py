from datetime import datetime
from decimal import Decimal

import pytest

from pit8c.io.xlsx import read_trades_from_xlsx, write_closed_positions_to_xlsx
from pit8c.models import ClosedPosition


@pytest.mark.parametrize(
    "closed_positions",
    [
        [
            ClosedPosition(
                isin="ABC123",
                ticker="TCK1",
                currency="USD",
                buy_date=datetime(2024, 1, 1),
                quantity=Decimal("10"),
                buy_amount=Decimal("1000"),
                sell_date=datetime(2024, 1, 2),
                sell_amount=Decimal("1200"),
            )
        ],
    ],
)
def test_write_and_read_xlsx(tmp_path, closed_positions):
    test_file = tmp_path / "test_output.xlsx"

    write_closed_positions_to_xlsx(closed_positions, [], test_file)
    assert test_file.exists()

    data = read_trades_from_xlsx(test_file)
    assert len(data) == len(closed_positions)

    for i, row in enumerate(data):
        cp = closed_positions[i]
        assert row["ISIN"] == cp.isin
        assert row["Ticker"] == cp.ticker
        assert row["Currency"] == cp.currency
        assert row["BuyDate"] == cp.buy_date.strftime("%Y-%m-%d")
        assert row["Quantity"] == str(cp.quantity)
        assert row["BuyAmount"] == str(cp.buy_amount)
        assert row["SellAmount"] == str(cp.sell_amount)
