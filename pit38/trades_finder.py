from datetime import datetime
from typing import Any


def match_trades_fifo(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Match buy–sell trades with FIFO approach. Returns a list of closed positions,
    each describing рow a buy-lot was closed (partially or fully) by a sell-lot.
    """

    # sort trades in ascending order of date and number
    trades_sorted = sorted(trades, key=lambda x: (x.get("ISIN", ""), x.get("Date", datetime.min), x.get("TradeNum", 0)))

    # FIFO queue: {ISIN: [ {remaining_qty, buy_date, buy_amount, buy_commission_value, ...}, ...]}
    open_positions: dict[str, list[dict]] = {}

    results = []

    for trade in trades_sorted:
        isin = trade.get("ISIN", "")
        if not isin:
            continue

        direction = trade.get("Direction", "").lower()  # "buy" / "sell"
        qty = trade.get("Quantity", 0.0)
        amount = trade.get("Amount", 0.0)
        date = trade.get("Date", None)
        if date is None:
            continue

        comm_value = trade.get("CommissionValue", 0.0)
        comm_curr = trade.get("CommissionCurrency", "")
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
                    "buy_comm_value": comm_value,
                    "buy_comm_currency": comm_curr,
                    "ticker": ticker,
                    "currency": currency,
                }
            )

        elif direction == "sell":
            # close position (partially or fully)
            to_close = qty
            sell_qty = qty
            sell_amount = amount
            sell_date = date
            sell_comm_value = comm_value

            if isin not in open_positions:
                continue

            fifo_queue = open_positions[isin]

            while to_close > 0 and fifo_queue:
                current_buy = fifo_queue[0]
                if current_buy["remaining_qty"] <= 0:
                    fifo_queue.pop(0)
                    continue

                available = current_buy["remaining_qty"]
                closed_lot = min(to_close, available)

                # the share of this position that we're in the process of closing
                portion = closed_lot / available

                # calculate the proportional part of BuyAmount, BuyCommission
                buy_amount_portion = current_buy["buy_amount"] * portion
                buy_comm_portion = current_buy["buy_comm_value"] * portion

                # same on the sell side
                sell_amount_portion = sell_amount * (closed_lot / sell_qty)
                sell_comm_portion = sell_comm_value * (closed_lot / sell_qty)

                total_commission = buy_comm_portion + sell_comm_portion

                results.append(
                    {
                        "ISIN": isin,
                        "Ticker": ticker,
                        "Currency": currency,
                        "BuyAmount": buy_amount_portion,
                        "BuyDate": current_buy["buy_date"],
                        "SellAmount": sell_amount_portion,
                        "SellDate": sell_date,
                        "TotalCommission": total_commission,
                    }
                )

                current_buy["remaining_qty"] -= closed_lot
                to_close -= closed_lot

                # if fully closed
                if current_buy["remaining_qty"] <= 0:
                    fifo_queue.pop(0)

    return results
