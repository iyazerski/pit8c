# PIT-8C

`pit8c` is a command-line tool that assists you in preparing the Polish [PIT-8C](https://www.pit.pl/pit-8c/)
declaration for investment income. It transforms raw broker reports into tax-ready documents by handling
complex calculations, currency conversions, and FIFO trade matching - all while adhering to Polish tax regulations.

---

## Table of Contents

- [Example Use Case](#example-use-case)
- [Installation](#installation)
- [Usage](#usage)
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
pit8c freedom24 annual_report_2024.xlsx
```

The tool automatically:
- Processes all trades from the XLSX report
- Matches sales with purchases using FIFO
- Applies correct NBP exchange rates (even for weekend trades)
- Generates ready-to-submit [PIT-8C](https://www.pit.pl/pit-8c/) (.pdf file)
- Creates audit-ready XLSX with all calculations

No more spreadsheet errors or manual rate lookups. 🚀

---

## Installation

- **Python 3.10 or later** is required.

### Using `pip` (from `PyPi`)

1. Install via `pip`:

   ```bash
   pip install pit8c
   ```

2. Now you can use the `pit8c` command:

   ```bash
   pit8c --help
   ```

### Using Poetry (only for developers)

1. Clone this repository:

   ```bash
   git clone https://github.com/iyazerski/pit8c.git
   cd pit8c
   ```

2. Install dependencies via [Poetry](https://python-poetry.org/):

   ```bash
   poetry install
   ```

3. To run the CLI:

   ```bash
   pit8c --help
   ```

---

## Usage

### Processing an Annual Report

To process your annual tax report (.xlsx file with all the trades made during the year), use:

```bash
pit8c <broker> <tax_report_file>
```

- **broker**: the broker’s name (lowercase).
- **tax_report_file**: the XLSX file with all your trades downloaded from the supported broker.

The tool will:

1. Read the broker’s XLSX file.
2. Convert all trades (buy and sell) into an internal unified structure based on ISIN and currency.
3. Apply FIFO matching to determine partial closures.
4. Compute income and costs for each matched position.
5. Generate PIT-8C PDF report and save it near the input file.
6. Print D section of PIT-8C report to console.
7. Write the closed positions near the input file (for audit).

**Example**:

```bash
pit8c freedom24 annual_report_2024.xlsx
```

---

## Testing

We use [pytest](https://docs.pytest.org/) for testing. Critical logic parts are covered (e.g. FIFO algorithm, trades parsing).

To run the tests:

```bash
poetry run pytest
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
