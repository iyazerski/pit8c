from pit38.models import ClosedPosition, DirectionEnum, Trade


def match_trades_fifo(trades: list[Trade]) -> list[ClosedPosition]:
    """
    Match buy–sell trades with FIFO approach.

    Input: List[Trade] (Pydantic model).
    Output: List[ClosedPosition], describing each partial/full closure.
    """

    trades_sorted = sorted(trades, key=lambda t: (t.isin, t.currency, t.trade_num))

    # { (isin, currency): [dict with remaining_qty, buy_date, buy_amount, comm_value, ...], ... }
    open_positions: dict[tuple[str, str], list[dict]] = {}

    results: list[ClosedPosition] = []

    for trade in trades_sorted:
        if not trade.isin or not trade.currency:
            continue

        key = (trade.isin, trade.currency)
        if trade.direction == DirectionEnum.buy:
            if key not in open_positions:
                open_positions[key] = []
            open_positions[key].append(
                {
                    "remaining_qty": trade.quantity,
                    "buy_date": trade.date,
                    "buy_amount": trade.amount,
                    "buy_comm_value": trade.commission_value,
                    "buy_comm_currency": trade.commission_currency,
                    "ticker": trade.ticker,
                    "currency": trade.currency,
                }
            )

        elif trade.direction == DirectionEnum.sell:
            if key not in open_positions:
                continue

            to_close = trade.quantity
            fifo_queue = open_positions[key]

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

                sell_amount_portion = trade.amount * (closed_lot / trade.quantity)
                sell_comm_portion = trade.commission_value * (closed_lot / trade.quantity)

                closed_pos = ClosedPosition(
                    isin=trade.isin,
                    ticker=trade.ticker,
                    currency=trade.currency,
                    buy_date=current_buy["buy_date"],
                    quantity=closed_lot,
                    buy_amount=buy_amount_portion,
                    sell_date=trade.date,
                    sell_amount=sell_amount_portion,
                    buy_commission=buy_comm_portion,
                    sell_commission=sell_comm_portion,
                )
                results.append(closed_pos)

                current_buy["remaining_qty"] = available - closed_lot
                to_close = to_close - closed_lot

                if current_buy["remaining_qty"] <= 0:
                    fifo_queue.pop(0)

    return results
