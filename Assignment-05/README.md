# Expense calculator

A small command line tool to keep track of personal expenses in KZT.
It uses only the Python standard library. No extra packages are required.
Python 3.10 or newer is recommended.

## How to run

Run commands from this folder:

    python cli.py add --date 2026-11-01 --category food --amount 1200 --note coffee
    python cli.py list
    python cli.py total
    python cli.py by-category
    python cli.py monthly --month 2026-11
    python cli.py export --format text --out report.txt
    python cli.py split --people 2

The default data file is `expenses.csv` in the current folder. You can point to another file with `--file`, for example `--file sample.csv`. For experiments, use a scratch copy, not `sample.csv`.

Dates must be written as YYYY-MM-DD. Amounts are in KZT and must be a plain number, 0 or more (use a dot, not a comma: `800.50`).

## Tests

    python -m unittest discover -v

## Assignment folder and git tags

This project lives in the `Assignment-05` folder so the repository can also hold later course assignments. The tags `baseline` (commit `64ce21a`) and `final` (commit `945ce31`) point to the original commits, when these files were still at the repository root.

- Baseline: https://github.com/dantemustd1e/Software-Engineering-Fall-2026/tree/baseline
- Final (the reviewed program): https://github.com/dantemustd1e/Software-Engineering-Fall-2026/tree/final
- Compare: https://github.com/dantemustd1e/Software-Engineering-Fall-2026/compare/baseline...final

The assignment PDFs, test logs, and AI prompts are in [`docs/`](docs/).

