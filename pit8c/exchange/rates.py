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

        currencies_needed.add(cp.currency)

    exchange = NbpExchange()
    for yr in sorted(years_needed):
        exchange.load_year(yr, currencies_needed)

    for cp in closed_positions:
        curr = cp.currency

        cp.buy_exchange_rate = exchange.get_rate_for(cp.buy_date.date(), curr, use_previous_day=True)
        cp.sell_exchange_rate = exchange.get_rate_for(cp.sell_date.date(), curr, use_previous_day=True)

    return closed_positions
