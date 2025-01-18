from datetime import datetime
from typing import Any


def match_trades_fifo(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Match buy–sell trades with FIFO approach.

    Returns:
      A list of closed positions. Each position is a dict with fields:
        - ISIN
        - Ticker
        - Currency
        - BuyAmount
        - BuyDate
        - SellAmount
        - SellDate
        - TotalCommission
      (One row for each partial or full close)
    """

    # sort by ISIN, then by Date, then by TradeNum
    trades_sorted = sorted(
        trades,
        key=lambda x: (x["ISIN"], x["Date"] if x["Date"] else datetime.min, x["TradeNum"]),
    )

    # FIFO queue: key=ISIN, value=list(dict(remaining_qty, buy_date, ...))
    open_positions: dict[str, list[dict]] = {}

    results = []

    for trade in trades_sorted:
        isin = trade.get("ISIN", "")
        if not isin:
            continue

        direction = trade.get("Direction", "")
        qty = trade.get("Quantity", 0.0)
        amount = trade.get("Amount", 0.0)
        date = trade.get("Date")
        if date is None:
            continue

        commission_value = trade.get("CommissionValue", 0.0)
        commission_currency = trade.get("CommissionCurrency", "")
        ticker = trade.get("Ticker", "")
        currency = trade.get("Currency", "")

        if direction == "buy":
            # put it on the list of open positions
            if isin not in open_positions:
                open_positions[isin] = []

            open_positions[isin].append(
                {
                    "remaining_qty": qty,
                    "buy_date": date,
                    "buy_amount": amount,
                    "buy_commission_value": commission_value,
                    "buy_commission_currency": commission_currency,
                    "ticker": ticker,
                    "currency": currency,
                }
            )

        elif direction == "sell":
            if isin not in open_positions:
                continue

            to_close = qty  # how much more to close
            sell_qty = qty
            sell_amount = amount
            sell_date = date
            sell_comm_value = commission_value

            fifo_list = open_positions[isin]

            while to_close > 0 and fifo_list:
                open_pos = fifo_list[0]
                if open_pos["remaining_qty"] <= 0:
                    fifo_list.pop(0)
                    continue

                available = open_pos["remaining_qty"]
                closed_lot = min(to_close, available)

                portion = closed_lot / available

                # buy side
                buy_amt_portion = open_pos["buy_amount"] * portion
                buy_comm_portion = open_pos["buy_commission_value"] * portion

                # sell side
                sell_amt_portion = sell_amount * (closed_lot / sell_qty)
                sell_comm_portion = sell_comm_value * (closed_lot / sell_qty)

                total_commission = buy_comm_portion + sell_comm_portion

                results.append(
                    {
                        "ISIN": isin,
                        "Ticker": ticker,
                        "Currency": currency,
                        "BuyAmount": buy_amt_portion,
                        "BuyDate": open_pos["buy_date"],
                        "SellAmount": sell_amt_portion,
                        "SellDate": sell_date,
                        "TotalCommission": total_commission,
                    }
                )

                # reduce "remaining_qty"
                open_pos["remaining_qty"] -= closed_lot
                to_close -= closed_lot

                # if fully closed
                if open_pos["remaining_qty"] <= 0:
                    fifo_list.pop(0)

    return results
