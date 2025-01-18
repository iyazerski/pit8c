from pit38.models import ClosedPosition, DirectionEnum, Trade


def match_trades_fifo(trades: list[Trade]) -> list[ClosedPosition]:
    """
    Match buy–sell trades with FIFO approach.

    Input: List[Trade] (Pydantic model).
    Output: List[ClosedPosition], describing each partial/full closure.
    """

    trades_sorted = sorted(trades, key=lambda t: (t.ISIN, t.Date, t.TradeNum))

    # { isin: [dict with remaining_qty, buy_date, buy_amount, comm_value, ...], ... }
    open_positions: dict[str, list[dict]] = {}

    results: list[ClosedPosition] = []

    for trade in trades_sorted:
        if not trade.ISIN:
            continue

        if trade.Direction == DirectionEnum.buy:
            if trade.ISIN not in open_positions:
                open_positions[trade.ISIN] = []
            open_positions[trade.ISIN].append(
                {
                    "remaining_qty": trade.Quantity,
                    "buy_date": trade.Date,
                    "buy_amount": trade.Amount,
                    "buy_comm_value": trade.CommissionValue,
                    "buy_comm_currency": trade.CommissionCurrency,
                    "ticker": trade.Ticker,
                    "currency": trade.Currency,
                }
            )

        elif trade.Direction == DirectionEnum.sell:
            if trade.ISIN not in open_positions:
                continue

            to_close = trade.Quantity
            sell_qty = trade.Quantity
            sell_amount = trade.Amount
            sell_date = trade.Date
            sell_comm_value = trade.CommissionValue
            ticker = trade.Ticker
            currency = trade.Currency

            fifo_queue = open_positions[trade.ISIN]
            while to_close > 0 and fifo_queue:
                current_buy = fifo_queue[0]
                if current_buy["remaining_qty"] <= 0:
                    fifo_queue.pop(0)
                    continue

                available = current_buy["remaining_qty"]
                closed_lot = min(to_close, available)

                portion = closed_lot / available

                buy_amount_portion = current_buy["buy_amount"] * portion
                buy_comm_portion = current_buy["buy_comm_value"] * portion

                sell_amount_portion = sell_amount * (closed_lot / sell_qty)
                sell_comm_portion = sell_comm_value * (closed_lot / sell_qty)

                total_commission = buy_comm_portion + sell_comm_portion

                closed_pos = ClosedPosition(
                    ISIN=trade.ISIN,
                    Ticker=ticker,
                    Currency=currency,
                    BuyDate=current_buy["buy_date"],
                    Quantity=closed_lot,
                    BuyAmount=buy_amount_portion,
                    SellDate=sell_date,
                    SellAmount=sell_amount_portion,
                    TotalCommission=total_commission,
                )
                results.append(closed_pos)

                current_buy["remaining_qty"] = available - closed_lot
                to_close = to_close - closed_lot

                if current_buy["remaining_qty"] <= 0:
                    fifo_queue.pop(0)

    return results
