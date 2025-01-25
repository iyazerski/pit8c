# PIT-38

**PIT-38** is a command-line tool that assists you in preparing the Polish PIT-38 declaration based on annual tax reports provided by your broker.
Currently, it supports **Freedom24**, but the architecture is designed to be extended for other brokers in the future.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

1. **Simple CLI**: A straightforward command-line interface built using [Typer](https://typer.tiangolo.com/).
2. **Freedom24 XLSX Support**: Reads Freedom24’s Excel annual tax report files and converts them into a standard format.
3. **FIFO Matching**: Automatically applies the First-In-First-Out logic to match buy and sell trades (including partial closures).
4. **Commission Handling**: Splits and sums commissions from both buy and sell sides, proportionally for partial trades.
5. **PIT-8C**: Generates PIT-8C PDF file with the income and costs values calculated based on the trades provided.
6. **Audit**: Exports all closed positions (buy date, buy amount, sell date, sell amount, total commission) in a XLSX file for audit.

---

## Installation

- **Python 3.10 or later** is required.

### Using `pip` (from `PyPi`)

1. Install via `pip`:

   ```bash
   pip install pit38
   ```

2. Now you can use the `pit38` command:

   ```bash
   pit38 --help
   ```

### Using Poetry (local repository)

1. Clone this repository:

   ```bash
   git clone https://github.com/iyazerski/pit38.git
   cd pit38
   ```

2. Install dependencies via [Poetry](https://python-poetry.org/):

   ```bash
   poetry install
   ```

3. To run the CLI:

   ```bash
   pit38 --help
   ```

---

## Usage

### Processing an Annual Report

To process your annual tax report (.xlsx file with all the trades made during the year), use:

```bash
pit38 <broker> <tax_report_file>
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
pit38 freedom24 annual_report_2024.xlsx
```

---

## Testing

We use [pytest](https://docs.pytest.org/) for testing and [Typer Testing](https://typer.tiangolo.com/tutorial/testing/) for CLI tests.

From the project root:

```bash
poetry install
poetry run pytest
```

---

## Contributing

Contributions are welcome! Please open an [issue](https://github.com/iyazerski/pit38/issues) or create a pull request:

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
