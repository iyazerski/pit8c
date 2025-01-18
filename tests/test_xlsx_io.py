from datetime import datetime

import pytest

from pit38.xlsx_io import read_trades_from_xlsx, write_trades_to_xlsx


@pytest.mark.parametrize(
    "closed_positions",
    [
        [
            {
                "ISIN": "ABC123",
                "Ticker": "TICK1",
                "Currency": "USD",
                "BuyAmount": 1000.0,
                "BuyDate": datetime(2024, 1, 1),
                "SellAmount": 1200.0,
                "SellDate": datetime(2024, 2, 1),
                "TotalCommission": 15.0,
            }
        ],
        [
            {
                "ISIN": "XYZ999",
                "Ticker": "TCKR2",
                "Currency": "EUR",
                "BuyAmount": 500.0,
                "BuyDate": datetime(2024, 5, 10),
                "SellAmount": 700.0,
                "SellDate": datetime(2024, 6, 1),
                "TotalCommission": 12.34,
            },
            {
                "ISIN": "XYZ999",
                "Ticker": "TCKR2",
                "Currency": "EUR",
                "BuyAmount": 600.0,
                "BuyDate": datetime(2024, 7, 10),
                "SellAmount": 900.0,
                "SellDate": datetime(2024, 8, 1),
                "TotalCommission": 15.67,
            },
        ],
    ],
)
def test_write_and_read_xlsx(tmp_path, closed_positions):
    test_file = tmp_path / "test_output.xlsx"

    write_trades_to_xlsx(closed_positions, test_file.as_posix())
    assert test_file.exists()

    data = read_trades_from_xlsx(str(test_file))

    assert len(data) == len(closed_positions)

    for i, row in enumerate(data):
        expected = closed_positions[i]

        buy_date_str = expected["BuyDate"].strftime("%Y-%m-%d")
        sell_date_str = expected["SellDate"].strftime("%Y-%m-%d")

        assert row["ISIN"] == expected["ISIN"]
        assert row["Ticker"] == expected["Ticker"]
        assert row["Currency"] == expected["Currency"]

        assert pytest.approx(row["BuyAmount"], 0.0001) == expected["BuyAmount"]
        assert row["BuyDate"] == buy_date_str
        assert pytest.approx(row["SellAmount"], 0.0001) == expected["SellAmount"]
        assert row["SellDate"] == sell_date_str
        assert pytest.approx(row["TotalCommission"], 0.0001) == expected["TotalCommission"]
