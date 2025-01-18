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
5. **XLSX Output**: Exports final summarized results (buy date, buy amount, sell date, sell amount, total commission) in a standardized XLSX file.

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

To process your annual tax report (from Freedom24), use:

```bash
pit38 freedom24 /path/to/input_file.xlsx /path/to/output_file.xlsx
```

- **freedom24**: the broker’s name (lowercase).
- **/path/to/input_file.xlsx**: the XLSX file downloaded from Freedom24 (or another supported broker, once implemented).
- **/path/to/output_file.xlsx**: the resulting XLSX file with matched buy-sell trades and commissions.

The tool will:

1. Read the broker’s XLSX file.
2. Convert all trades (buy and sell) into an internal unified structure.
3. Apply FIFO matching to determine partial closures.
4. Compute total commissions for each matched position.
5. Write the finalized trades into `output_file.xlsx`.

**Example**:

```bash
pit38 process freedom24 annual_report_2024.xlsx closed_positions_2024.xlsx
```

---

## Testing

We use [pytest](https://docs.pytest.org/) for testing and [Typer Testing](https://typer.tiangolo.com/tutorial/testing/) for CLI tests.

1. From the project root:

   ```bash
   poetry install
   poetry run pytest
   ```

2. Tests are located in the `tests/` directory and include:

   - **CLI tests**: `test_cli.py`
   - **FIFO logic tests**: `test_trades_finder.py`
   - **XLSX read/write tests**: `test_xlsx_io.py`

All tests use the built-in `tmp_path` fixture to handle temporary files.

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
