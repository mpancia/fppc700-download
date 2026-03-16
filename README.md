# fppc700-download

A CLI tool to download [Form 700](https://www.fppc.ca.gov/Form700.html) PDF reports from the [California Fair Political Practices Commission database](https://form700search.fppc.ca.gov).

```sh
Usage: fppc700-download [OPTIONS]

Options:
  --filer-first-name TEXT         First name starts with search query
  --filer-last-name TEXT          Last name starts with search query
  --filer-position TEXT           Filer's position, default is "Assembly Member"
  --filing-year INTEGER           Year for data in report
  --output-directory TEXT         Path to destination directory of PDF files, default is .
  --amendments-only               Only search for Amendment filings
  --currently-held-positions-only Limit to reports by filers with a current position
  --ignore-existing-files         Only download files that don't exist in output directory
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
