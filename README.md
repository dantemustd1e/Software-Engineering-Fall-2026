# Expense calculator

A small command line tool to keep track of personal expenses in KZT.

## How to run

Python 3.10 or newer is required.

    python main.py add --date 2026-11-01 --category food --amount 1200 --note coffee
    python main.py list
    python main.py total
    python main.py by-category
    python main.py monthly --month 2026-11
    python main.py export --format text --out report.txt

The default data file is `expenses.csv` in the current folder.

Dates should be written as YYYY-MM-DD. Amounts are in KZT.

## Tests

    python -m unittest discover -v
