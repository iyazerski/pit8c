from datetime import datetime

import pytest

from pit38.trades_finder import match_trades_fifo


@pytest.mark.parametrize(
    "trades, positions_num, expected_total_commission",
    [
        (
            # buy->sell all
            [
                {
                    "ISIN": "TEST123",
                    "TradeNum": "123",
                    "Direction": "buy",
                    "Date": datetime(2024, 1, 1),
                    "Quantity": 10,
                    "Amount": 1000.0,
                    "CommissionValue": 10.0,
                },
                {
                    "ISIN": "TEST123",
                    "TradeNum": "124",
                    "Direction": "sell",
                    "Date": datetime(2024, 2, 1),
                    "Quantity": 10,
                    "Amount": 1200.0,
                    "CommissionValue": 5.0,
                },
            ],
            1,
            [15.0],  # 10 (buy) + 5 (sell)
        ),
        (
            # 2x buy, 1 partial sell
            [
                {
                    "ISIN": "XYZ999",
                    "TradeNum": "997",
                    "Direction": "buy",
                    "Date": datetime(2024, 1, 10),
                    "Quantity": 5,
                    "Amount": 500.0,
                    "CommissionValue": 5.0,
                },
                {
                    "ISIN": "XYZ999",
                    "TradeNum": "998",
                    "Direction": "buy",
                    "Date": datetime(2024, 1, 15),
                    "Quantity": 5,
                    "Amount": 600.0,
                    "CommissionValue": 6.0,
                },
                {
                    "ISIN": "XYZ999",
                    "TradeNum": "999",
                    "Direction": "sell",
                    "Date": datetime(2024, 2, 1),
                    "Quantity": 8,
                    "Amount": 1000.0,
                    "CommissionValue": 10.0,
                },
            ],
            2,
            [11.25, 7.35],
        ),
    ],
)
def test_match_trades_fifo(trades, positions_num, expected_total_commission):
    """
    Check FIFO matching with different trade sets.
    """
    results = match_trades_fifo(trades)

    assert len(results) == positions_num
    for i in range(positions_num):
        assert pytest.approx(results[i]["TotalCommission"], 0.0001) == expected_total_commission[i]
