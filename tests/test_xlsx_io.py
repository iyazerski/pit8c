from datetime import datetime
from decimal import Decimal

import pytest

from pit38.models import ClosedPosition
from pit38.xlsx_io import read_trades_from_xlsx, write_trades_to_xlsx


@pytest.mark.parametrize(
    "closed_positions",
    [
        [
            ClosedPosition(
                ISIN="ABC123",
                Ticker="TCK1",
                Currency="USD",
                BuyDate=datetime(2024, 1, 1),
                Quantity=Decimal("10"),
                BuyAmount=Decimal("1000"),
                SellDate=datetime(2024, 1, 2),
                SellAmount=Decimal("1200"),
                TotalCommission=Decimal("15"),
            )
        ],
    ],
)
def test_write_and_read_xlsx(tmp_path, closed_positions):
    test_file = tmp_path / "test_output.xlsx"

    write_trades_to_xlsx(closed_positions, str(test_file))
    assert test_file.exists()

    data = read_trades_from_xlsx(str(test_file))
    assert len(data) == len(closed_positions)

    for i, row in enumerate(data):
        cp = closed_positions[i]
        assert row["ISIN"] == cp.ISIN
        assert row["Ticker"] == cp.Ticker
        assert row["Currency"] == cp.Currency
        assert row["BuyDate"] == cp.BuyDate.strftime("%Y-%m-%d")
        assert row["Quantity"] == str(cp.Quantity)
        assert row["BuyAmount"] == str(cp.BuyAmount)
        assert row["SellAmount"] == str(cp.SellAmount)
        assert row["TotalCommission"] == str(cp.TotalCommission)
