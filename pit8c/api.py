from decimal import Decimal
from pathlib import Path

from pit8c.brokers.base import BrokerAdapter, SupportedBroker
from pit8c.brokers.registry import get_broker_adapter
from pit8c.exceptions import Pit8cError
from pit8c.exchange.provider import ExchangeRatesProvider, NbpExchangeRatesProvider
from pit8c.exchange.rates import fill_exchange_rates
from pit8c.io.xlsx import write_closed_positions_to_xlsx
from pit8c.models import ClosedPosition, Trade
from pit8c.pipeline import load_trades_from_reports_path, match_trades_and_select_tax_year
from pit8c.positions.profit_calculator import calculate_profit
from pit8c.reports.pit_8c import Pit8cReportGenerator, TemplatePit8cReportGenerator
from pit8c.result import Pit8cArtifacts, Pit8cResult, Pit8cTotals


class Pit8c:
    """High-level PIT-8C pipeline runner usable from code and from the CLI."""

    def __init__(
        self,
        broker: SupportedBroker | str | None = None,
        adapter: BrokerAdapter | None = None,
        exchange_provider: ExchangeRatesProvider | None = None,
        report_generator: Pit8cReportGenerator | None = None,
        output_dir: Path | None = None,
        write_pdf: bool = True,
        write_xlsx: bool = True,
    ) -> None:
        """Create a configured PIT-8C runner with optional defaults for subsequent runs."""

        self._broker = self._parse_broker(broker) if broker is not None else None
        self._adapter = adapter
        self._exchange_provider = exchange_provider or NbpExchangeRatesProvider()
        self._report_generator = report_generator or TemplatePit8cReportGenerator()
        self._output_dir = output_dir
        self._write_pdf = write_pdf
        self._write_xlsx = write_xlsx

    def process_reports_path(self, reports_path: Path, tax_year: int) -> Pit8cResult:
        """Read broker report XLSX file(s), compute PIT-8C results and optionally write output artifacts."""

        adapter = self._resolve_adapter()
        input_reports, trades = load_trades_from_reports_path(adapter, reports_path)

        output_dir = self._output_dir or (reports_path.parent if reports_path.is_file() else reports_path)
        output_stem = reports_path.stem if reports_path.is_file() else reports_path.name
        output_base = f"{output_stem}_{tax_year}"

        return self._process_trades(
            trades=trades,
            tax_year=tax_year,
            input_reports=input_reports,
            output_dir=output_dir,
            output_base=output_base,
        )

    def process_trades(
        self,
        trades: list[Trade],
        tax_year: int,
        output_base: str = "pit8c",
        output_dir: Path | None = None,
    ) -> Pit8cResult:
        """Run PIT-8C pipeline for already parsed trades (no XLSX read), optionally writing artifacts."""

        resolved_output_dir = output_dir or self._output_dir
        return self._process_trades(
            trades=trades,
            tax_year=tax_year,
            input_reports=[],
            output_dir=resolved_output_dir,
            output_base=f"{output_base}_{tax_year}",
        )

    def _resolve_adapter(self) -> BrokerAdapter:
        if self._adapter is not None:
            return self._adapter
        if self._broker is None:
            raise Pit8cError("Broker adapter is not configured")
        return get_broker_adapter(self._broker)

    def _process_trades(
        self,
        trades: list[Trade],
        tax_year: int,
        input_reports: list[Path],
        output_dir: Path | None,
        output_base: str,
    ) -> Pit8cResult:
        closed_positions = match_trades_and_select_tax_year(trades, tax_year)

        fill_exchange_rates(closed_positions, provider=self._exchange_provider)
        profit_positions, loss_positions = calculate_profit(closed_positions)
        totals = self._compute_totals(closed_positions)
        pit8c_text = self._report_generator.render_text(totals)

        pit8c_pdf_path: Path | None = None
        closed_positions_xlsx_path: Path | None = None

        writable_output_dir: Path | None = None
        if self._write_pdf or self._write_xlsx:
            if output_dir is None:
                raise Pit8cError("output_dir must be provided when output writing is enabled")
            writable_output_dir = output_dir.resolve()
            writable_output_dir.mkdir(parents=True, exist_ok=True)

        if self._write_pdf:
            if writable_output_dir is None:
                raise Pit8cError("output_dir must be provided when output writing is enabled")
            pit8c_pdf_path = writable_output_dir / f"{output_base}_pit_8c.pdf"
            self._report_generator.write_pdf(totals, pit8c_pdf_path)

        if self._write_xlsx:
            if writable_output_dir is None:
                raise Pit8cError("output_dir must be provided when output writing is enabled")
            closed_positions_xlsx_path = writable_output_dir / f"{output_base}_closed_positions.xlsx"
            write_closed_positions_to_xlsx(profit_positions, loss_positions, closed_positions_xlsx_path)

        artifacts = Pit8cArtifacts(
            pit8c_text=pit8c_text,
            pit8c_pdf_path=pit8c_pdf_path,
            closed_positions_xlsx_path=closed_positions_xlsx_path,
        )

        return Pit8cResult(
            tax_year=tax_year,
            input_reports=input_reports,
            trades=trades,
            closed_positions=closed_positions,
            profit_positions=profit_positions,
            loss_positions=loss_positions,
            totals=totals,
            artifacts=artifacts,
        )

    @staticmethod
    def _compute_totals(closed_positions: list[ClosedPosition]) -> Pit8cTotals:
        """Compute aggregated income/costs/profit totals in PLN from closed positions."""

        total_income = sum((cp.income_pln for cp in closed_positions), Decimal(0)).quantize(Decimal("0.01"))
        total_costs = sum((cp.costs_pln for cp in closed_positions), Decimal(0)).quantize(Decimal("0.01"))
        profit = (total_income - total_costs).quantize(Decimal("0.01"))
        return Pit8cTotals(income_pln=total_income, costs_pln=total_costs, profit_pln=profit)

    @staticmethod
    def _parse_broker(value: SupportedBroker | str) -> SupportedBroker:
        """Parse a SupportedBroker from an enum value or a string."""

        if isinstance(value, SupportedBroker):
            return value
        try:
            return SupportedBroker(value)
        except ValueError as exc:
            allowed = ", ".join(b.value for b in SupportedBroker)
            raise Pit8cError(f"Unsupported broker '{value}'. Supported brokers: {allowed}") from exc
