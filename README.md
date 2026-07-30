# fppc700-download

A CLI tool to download [Form 700](https://www.fppc.ca.gov/Form700.html) PDF reports from the [California Fair Political Practices Commission database](https://form700search.fppc.ca.gov).

**Note:** This tool is currently a prototype and may not be further developed.

```sh
Usage: fppc700-download [OPTIONS]

Options:
  --filer-first-name TEXT         First name starts with search query
  --filer-last-name TEXT          Last name starts with search query
  --filer-position TEXT           Position of filer, default is "Assembly Member"
  --filing-year INTEGER           Year for data in report
  --output-directory TEXT         Path to destination directory of PDF files, default is .
  --amendments-only               Only search for Amendment filings
  --currently-held-positions-only Limit to reports by filers with a current position
  --ignore-existing-files         Only download files that do not exist in output directory
  --help                          Show this message and exit.
```

## Examples
The following command would download all of the 2025 FPPC Form 700 reports for judges who have a last name that starts with "K" into the current directory:

```sh
fppc700-download --filing-position Judge --filer-last-name K --filing-year 2025 --output-directory .
```

The following command would download all of the 2025 FPPC Form 700 reports for Assembly Members who are currently holding any position into the current directory, skipping any that have already been downloaded:

```sh
fppc700-download --filing-position "Assembly Member" --filing-year 2025 --output-directory . --currently-held-positions-only --ignore-existing-files
```

## Installation

You can install the CLI tool from this Github repository using `pip` or `uv`:

```sh
pip install git+https://github.com/CalMatters/fppc700-download.git
```

```sh
uv pip install "git+https://github.com/CalMatters/fppc700-download.git"
```

## Motivation

We made this tool because we needed it! And we're sharing it publicly in case other folks need it or have ideas for improvement.

We've gone through and extracted data from the Form 700 documents filed by the entire legislator the past few years (for filings regarding [2022](https://calmatters.org/politics/2023/05/california-legislature-trips-bills/), [2023](https://calmatters.org/politics/2024/06/california-legislator-stock-investment/), [2024](https://calmatters.org/digital-democracy/2025/09/california-legislature-sponsored-trips-israel/), [2025](https://calmatters.org/politics/2026/03/california-lawmakers-free-gifts-trips/)) in a relatively time-consuming process. However, starting in 2025 [AB1170](https://calmatters.digitaldemocracy.org/bills/ca_202320240ab1170) required legislators to submit their reports electronicly which means that all the documents have exactly the same layout.

## Development

Run the test suite with `uv run pytest`. Format all of the files with `uv run ruff format`.

## Please let us know if you use this tool!

If you end up using this tool, please get in touch and share your use case with us by sending an email to jeremia@calmatters.org.