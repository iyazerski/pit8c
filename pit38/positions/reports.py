from decimal import Decimal

from pit38.models import ClosedPosition

PIT_8C = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  PIT-8C                                     │
│ D. INFORMACJA O WYSOKOŚCI DOCHODÓW, O KTÓRYCH MOWA W ART. 30B UST. 2 USTAWY │
├────────────────────┬──────────────────┬──────────────────┬──────────────────┤
│ Rodzaje przychodów │    Przychód      │ Koszty uzyskania │     Dochód       │
│                    │                  │    przychodu     │     (b - c)      │
├────────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Razem              │ 35.              │ 36.              │ 37.              │
│                    │ {income:13} zł │ {costs:13} zł │ {net:13} zł │
└────────────────────┴──────────────────┴──────────────────┴──────────────────┘
"""


def print_pit8c(closed_positions: list[ClosedPosition]) -> None:
    total_income = Decimal("0.0")
    total_costs = Decimal("0.0")
    for cp in closed_positions:
        total_income += cp.income_pln
        total_costs += cp.costs_pln
    net_income = total_income - total_costs

    print(PIT_8C.format(income=str(total_income), costs=str(total_costs), net=str(net_income)).strip())
