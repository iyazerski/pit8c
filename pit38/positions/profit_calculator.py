from decimal import Decimal

from pit38.models import ClosedPosition


def calculate_profit(closed_positions: list[ClosedPosition]) -> list[ClosedPosition]:
    """
    Compute the profit in PLN for each closed position,
    taking into account exchange rates and commissions.

    Formula:
      buy_value_pln  = (buy_amount  + buy_commission)  * buy_exchange_rate
      sell_value_pln = (sell_amount - sell_commission) * sell_exchange_rate
      profit_pln     = sell_value_pln - buy_value_pln

    The profit is stored in the 'profit' field of the ClosedPosition.
    """
    total_profit = Decimal("0.0")

    for cp in closed_positions:
        # (BuyAmount + BuyCommission) * BuyExchangeRate
        buy_value = cp.buy_amount + cp.buy_commission
        buy_value_pln = buy_value * cp.buy_exchange_rate

        # (SellAmount - SellCommission) * SellExchangeRate
        sell_value = cp.sell_amount - cp.sell_commission
        sell_value_pln = sell_value * cp.sell_exchange_rate

        cp.profit = sell_value - buy_value
        cp.profit_pln = sell_value_pln - buy_value_pln
        total_profit += cp.profit_pln

    print(f"Total profit: {total_profit} PLN")
    return closed_positions
