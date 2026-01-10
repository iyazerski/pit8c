from pit8c.exchange.nbp import NbpExchange
from pit8c.models import ClosedPosition


def fill_exchange_rates(closed_positions: list[ClosedPosition]) -> list[ClosedPosition]:
    years_needed = set()
    currencies_needed = set()
    for cp in closed_positions:
        years_needed.add(cp.buy_date.year)
        years_needed.add(cp.sell_date.year)
        years_needed.add(cp.buy_date.year - 1)
        years_needed.add(cp.sell_date.year - 1)

        trade_currency = cp.currency
        buy_comm_currency = cp.buy_commission_currency or trade_currency
        sell_comm_currency = cp.sell_commission_currency or trade_currency

        currencies_needed.add(trade_currency)
        currencies_needed.add(buy_comm_currency)
        currencies_needed.add(sell_comm_currency)

    exchange = NbpExchange()
    for yr in sorted(years_needed):
        exchange.load_year(yr, currencies_needed)

    for cp in closed_positions:
        curr = cp.currency
        buy_comm_curr = cp.buy_commission_currency or curr
        sell_comm_curr = cp.sell_commission_currency or curr

        # Normalize currencies so downstream consumers can rely on non-empty codes.
        cp.buy_commission_currency = buy_comm_curr
        cp.sell_commission_currency = sell_comm_curr

        cp.buy_exchange_rate = exchange.get_rate_for(cp.buy_date.date(), curr, use_previous_day=True)
        cp.sell_exchange_rate = exchange.get_rate_for(cp.sell_date.date(), curr, use_previous_day=True)
        cp.buy_commission_exchange_rate = exchange.get_rate_for(
            cp.buy_date.date(), buy_comm_curr, use_previous_day=True
        )
        cp.sell_commission_exchange_rate = exchange.get_rate_for(
            cp.sell_date.date(), sell_comm_curr, use_previous_day=True
        )

    return closed_positions
