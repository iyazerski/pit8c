from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from pit8c.models import ClosedPosition, Trade


@dataclass(frozen=True, slots=True)
class Pit8cTotals:
    """Aggregated PIT-8C totals in PLN computed from closed positions."""

    income_pln: Decimal
    costs_pln: Decimal
    profit_pln: Decimal

    @property
    def is_profit(self) -> bool:
        """Return True when profit_pln is non-negative (otherwise it is a loss)."""

        return self.profit_pln >= 0


@dataclass(frozen=True, slots=True)
class Pit8cArtifacts:
    """Optional output artifacts produced by the pipeline."""

    pit8c_text: str | None = None
    pit8c_pdf_path: Path | None = None
    closed_positions_xlsx_path: Path | None = None


@dataclass(frozen=True, slots=True)
class Pit8cResult:
    """Result of PIT-8C processing run, including computed positions, totals and output artifacts."""

    tax_year: int
    input_reports: list[Path]
    trades: list[Trade]
    closed_positions: list[ClosedPosition]
    profit_positions: list[ClosedPosition]
    loss_positions: list[ClosedPosition]
    totals: Pit8cTotals
    artifacts: Pit8cArtifacts
