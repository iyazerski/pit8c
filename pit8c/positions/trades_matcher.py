from collections import deque
from datetime import datetime
from decimal import Decimal
from typing import TypedDict

from pit8c.exceptions import Pit8cError
from pit8c.models import ClosedPosition, DirectionEnum, Trade


class _OpenPosition(TypedDict):
    remaining_qty: Decimal
    buy_date: datetime
    remaining_buy_amount: Decimal
    remaining_buy_commission: Decimal
    buy_comm_currency: str
    ticker: str
    currency: str


def match_trades_fifo(trades: list[Trade]) -> list[ClosedPosition]:
    """
    Match buy–sell trades with FIFO approach.

    Input: List[Trade] (Pydantic model).
    Output: List[ClosedPosition], describing each partial/full closure.
    """

    # Sort deterministically and FIFO-correctly:
    # - group by (isin, currency)
    # - process in chronological order
    # - for same moment, process buys before sells
    trades_sorted = sorted(
        trades,
        key=lambda t: (
            t.isin,
            t.currency,
            t.date,
            0 if t.direction == DirectionEnum.buy else 1,
            t.trade_num,
        ),
    )

    # { (isin, currency): queue of buy-lots with remaining qty/amount/commission, ... }
    open_positions: dict[tuple[str, str], deque[_OpenPosition]] = {}

    results: list[ClosedPosition] = []

    for trade in trades_sorted:
        if not trade.isin or not trade.currency:
            continue
        if trade.quantity <= 0:
            raise Pit8cError(f"Trade quantity must be > 0, got {trade.quantity} for trade_num={trade.trade_num}")

        key = (trade.isin, trade.currency)
        if trade.direction == DirectionEnum.buy:
            if key not in open_positions:
                open_positions[key] = deque()
            open_positions[key].append(
                {
                    "remaining_qty": trade.quantity,
                    "buy_date": trade.date,
                    "remaining_buy_amount": trade.amount,
                    "remaining_buy_commission": trade.commission_value,
                    "buy_comm_currency": trade.commission_currency or trade.currency,
                    "ticker": trade.ticker,
                    "currency": trade.currency,
                }
            )

        elif trade.direction == DirectionEnum.sell:
            if key not in open_positions:
                raise Pit8cError(
                    f"Sell trade has no matching buy lots (isin={trade.isin}, currency={trade.currency}, "
                    f"trade_num={trade.trade_num})"
                )

            remaining_sell_qty = trade.quantity
            remaining_sell_amount = trade.amount
            remaining_sell_commission = trade.commission_value
            sell_comm_currency = trade.commission_currency or trade.currency
            fifo_queue = open_positions[key]

            while remaining_sell_qty > 0:
                if not fifo_queue:
                    raise Pit8cError(
                        f"Sell quantity exceeds available buy lots by {remaining_sell_qty} "
                        f"(isin={trade.isin}, currency={trade.currency}, trade_num={trade.trade_num})"
                    )

                current_buy = fifo_queue.popleft()
                if current_buy["remaining_qty"] <= 0:
                    continue

                available_buy_qty = current_buy["remaining_qty"]
                closed_lot = min(remaining_sell_qty, available_buy_qty)

                buy_portion = closed_lot / available_buy_qty
                sell_portion = closed_lot / remaining_sell_qty

                buy_amount_portion = current_buy["remaining_buy_amount"] * buy_portion
                buy_comm_portion = current_buy["remaining_buy_commission"] * buy_portion

                sell_amount_portion = remaining_sell_amount * sell_portion
                sell_comm_portion = remaining_sell_commission * sell_portion

                closed_pos = ClosedPosition(
                    isin=trade.isin,
                    ticker=current_buy["ticker"],
                    currency=trade.currency,
                    buy_date=current_buy["buy_date"],
                    quantity=closed_lot,
                    buy_amount=buy_amount_portion,
                    sell_date=trade.date,
                    sell_amount=sell_amount_portion,
                    buy_commission=buy_comm_portion,
                    sell_commission=sell_comm_portion,
                    buy_commission_currency=current_buy["buy_comm_currency"],
                    sell_commission_currency=sell_comm_currency,
                )
                results.append(closed_pos)

                current_buy["remaining_qty"] = available_buy_qty - closed_lot
                current_buy["remaining_buy_amount"] = current_buy["remaining_buy_amount"] - buy_amount_portion
                current_buy["remaining_buy_commission"] = current_buy["remaining_buy_commission"] - buy_comm_portion
                remaining_sell_qty = remaining_sell_qty - closed_lot
                remaining_sell_amount = remaining_sell_amount - sell_amount_portion
                remaining_sell_commission = remaining_sell_commission - sell_comm_portion

                # Keep the partially consumed lot at the head of the queue for subsequent matches.
                if current_buy["remaining_qty"] > 0:
                    fifo_queue.appendleft(current_buy)

    return results
