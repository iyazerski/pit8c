from decimal import Decimal

from pit38.models import ClosedPosition


def calculate_profit(closed_positions: list[ClosedPosition]) -> list[ClosedPosition]:
    """
    Compute the income and costs in PLN for each closed position,
    taking into account exchange rates.
    """
    for cp in closed_positions:
        # profit in trade currency
        cp.profit = cp.sell_amount - cp.buy_amount

        # Income (Przychód): Sell Amount * Sell Exchange Rate
        cp.income_pln = (cp.sell_amount * cp.sell_exchange_rate).quantize(Decimal("0.01"))

        # Costs (Koszty): (Buy Amount + Buy Commission) * Buy Rate + Sell Commission * Sell Rate
        buy_total_pln = (cp.buy_amount + cp.buy_commission) * cp.buy_exchange_rate
        sell_comm_pln = cp.sell_commission * cp.sell_exchange_rate
        cp.costs_pln = (buy_total_pln + sell_comm_pln).quantize(Decimal("0.01"))

    return closed_positions
