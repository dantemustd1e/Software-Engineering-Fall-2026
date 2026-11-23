# AGENTS.md

Instructions for a coding assistant that works on this repository.

## Purpose

This is a small command-line expense calculator. It stores personal expenses in KZT in a CSV file and can list them, print a total, group totals by category, show a monthly summary, export a report, and split the total between people.

Do not use real personal data or secrets in sample rows. The current samples (coffee, bus, and so on) are fictional.

## Architecture

- `expenses.py` — `Expense` model and the in-memory `ExpenseBook` (add, list, totals, monthly summary, split).
- `storage.py` — load and save the CSV file.
- `report.py` — text, CSV and monthly export.
- `cli.py` — the command-line entry point (`python cli.py ...`). There is no `main.py`.
- `tests/test_expenses.py` — unittest tests.
- `sample.csv` — fictional sample data. Prefer a scratch copy when trying write commands.

## Setup

- Python 3, standard library only. There is no `requirements.txt` and no third-party package.
- Run commands from the repository root so that `import expenses` works.
- Helpful commands:
  - `python cli.py --help`
  - `python cli.py --file sample.csv list`
  - `python -m unittest discover -v`
  - `python -m py_compile expenses.py storage.py report.py cli.py tests/test_expenses.py`

## Safe commands

These are safe to run without asking:

- `python -m unittest discover -v`
- `python -m py_compile` on the project files
- `python cli.py --help`
- `python cli.py --file <scratch.csv> list|total|by-category|monthly|export|split` when `<scratch.csv>` is a temporary copy, not the user's real file

Ask the human first before:

- writing to `sample.csv` or to the default `expenses.csv`
- adding or changing a dependency
- renaming or deleting source files
- running a large rewrite

## Coding conventions

- Keep the code in the standard library. Do not add packages unless the human agrees.
- Keep changes small and close to the current style.
- Dates should be `YYYY-MM-DD`. Amounts are in KZT.
- Tests use `unittest` (not pytest). Use a temporary file for save/load tests.

## Test expectations

- After a change, run `python -m unittest discover -v` and show the real output.
- Do not edit a test only to make a weak patch pass.
- If you add behaviour (validation, a new error message, a new export format), add a test for it.
- The acceptance criteria in the assignment notes must still hold: add/list keeps the same fields, totals are correct for whole-tenge amounts, monthly summary works for `YYYY-MM-DD` dates, and a CSV round-trip keeps the same fields.

## Forbidden actions

- Do not add, commit, print or ask for secrets, tokens, passwords, API keys or real personal data.
- Do not deploy this project to any server or production environment.
- Do not run destructive commands, including `rm -rf`, `git reset --hard`, `git checkout --` on files you did not just create, `git push --force`, or wiping a CSV data file.
- Do not add or change dependencies without a human review.
- Do not create a git commit unless the human asked for it.

## Review gates

- For any non-trivial change, show the diff and wait for approval before applying it.
- A task is not finished until the tests have been run and the output is shown.
- Do not tag a release or describe the project as ready to ship without a human decision.
- If a command could overwrite a data file, use a scratch copy first.
