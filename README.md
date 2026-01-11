# PIT-8C

`pit8c` is a command-line tool that assists you in preparing the Polish [PIT-8C](https://www.pit.pl/pit-8c/)
declaration for investment income. It transforms raw broker reports into tax-ready documents by handling
complex calculations, currency conversions, and FIFO trade matching - all while adhering to Polish tax regulations.

---

## Table of Contents

- [Example Use Case](#example-use-case)
- [Installation](#installation)
- [Usage](#usage)
- [Using as a Library](#using-as-a-library)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Example Use Case
*Marta, a Polish investor, made 200+ stock trades in 2024 through Freedom24, including US and EU stocks.
Since Freedom24 is based in Cyprus, it doesn't generate a PIT-8C declaration. So Marta needs to:*
1. Match each sale to its original purchase (including partial closures)
2. Convert all foreign amounts to PLN using NBP rates from transaction dates
3. Calculate total income/costs for tax declaration
4. Manually fill the PIT-8C declaration

*With pit8c, she simply runs:*
```bash
pit8c freedom24 ./reports --year 2024
```

The tool automatically:
- Reads one XLSX report or a directory with multiple annual reports
- Matches sales with purchases using FIFO
- Applies correct NBP exchange rates (even for weekend trades)
- Generates ready-to-submit [PIT-8C](https://www.pit.pl/pit-8c/) (.pdf file)
- Creates audit-ready XLSX with all calculations

No more spreadsheet errors or manual rate lookups. 🚀

---

## Installation

- **Python 3.11 or later** is required.

### Using `pip` (from `PyPi`)

1. Install via `pip`:

   ```bash
   pip install pit8c
   ```

2. Now you can use the `pit8c` command:

   ```bash
   pit8c --help
   ```

### Using uv (only for developers)

1. Clone this repository:

   ```bash
   git clone https://github.com/iyazerski/pit8c.git
   cd pit8c
   ```

2. Install dependencies via [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

3. To run the CLI:

   ```bash
   uv run pit8c --help
   ```

---

## Usage

### Processing an Annual Report

To calculate PIT-8C for a given tax year, pass either:
- a single annual report `.xlsx`, or
- a directory containing multiple annual reports `.xlsx` (recommended, so FIFO can match prior-year buys).

```bash
pit8c --broker <broker> --reports-path <reports_path> --year <tax_year>
```

- **broker**: the broker’s name (lowercase).
- **reports_path**: path to a single XLSX report or a directory with multiple reports.
- **tax_year**: the year for which PIT-8C should be calculated (only positions with sell date in that year are included).

The tool will:

1. Read one or more broker XLSX files.
2. Convert all trades (buy and sell) into an internal unified structure based on ISIN and currency.
3. Apply FIFO matching across all provided years to determine partial closures.
4. Select only positions closed (sold) in the requested tax year.
5. Compute income and costs for selected positions.
6. Generate PIT-8C PDF report and save it near the input path.
7. Print D section of PIT-8C report to console.
8. Write the closed positions near the input file (for audit).

**Example**:

```bash
pit8c --broker freedom24 --reports-path ./reports --year 2025
```

---

## Using as a Library

Use the `Pit8c` class to run the same pipeline from Python code:

```python
from pathlib import Path
from pit8c import Pit8c

pit8c = Pit8c(broker="freedom24")
result = pit8c.process_reports_path(reports_path=Path("./reports"), tax_year=2024)

print(result.totals.income_pln, result.totals.costs_pln)
print(result.artifacts.pit8c_pdf_path)
```

If you already have parsed trades, run the pipeline without reading XLSX:

```python
from pit8c import Pit8c

# trades: list[Trade]
pit8c = Pit8c(write_pdf=False, write_xlsx=False)
result = pit8c.process_trades(trades, tax_year=2024)
```

## Testing

We use [pytest](https://docs.pytest.org/) for testing. Critical logic parts are covered (e.g. FIFO algorithm, trades parsing).

To run the tests:

```bash
uv run pytest
```

---

## Contributing

Contributions are welcome! Please open an [issue](https://github.com/iyazerski/pit8c/issues) or create a pull request:

1. **Fork** the repository
2. **Create a feature branch**
3. **Commit** your changes
4. **Open a pull request** towards the `main` branch.

Be sure to include tests to cover new functionality or bug fixes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Disclaimer**:
This tool is provided as-is. The authors and contributors are not responsible for any inaccuracies or omissions in the tax calculations. Always consult a certified tax adviser or official resources to verify the correctness of your tax returns.
