I read the code but did not run it. "Confident" below means I traced it through the code by hand, and "unverified" means it depends on your OS, your spreadsheet app, or something I couldn't check. The paste has no line numbers, so I point to functions. Every check uses a scratch file (`--file scratch.csv` or a copy of `sample.csv`), so your real data stays untouched. L = likelihood and I = impact, both 1-3.

## Correctness

**C-01 Month filter is a prefix match** (confident)
- **Where:** `expenses.py`, `ExpenseBook.monthly_summary`, which uses `startswith`.
- **What can go wrong:** The month string is free text, so `--month 2026-1` matches Oct, Nov and Dec. `--month 2026` matches the whole year, and an empty string matches everything. The report then looks like a single month's total but isn't.
- **Check:** `python cli.py --file sample.csv monthly --month 2026-1`, then compare with `--month 2026-11`.
- **L2 / I2**

**C-02 No input validation on `add`** (confident)
- **Where:** `cli.cmd_add` and `ExpenseBook.add`, which use `float(amount)` and `str(date)`.
- **What can go wrong:**
  - A decimal comma (`--amount 800,50`) crashes with a raw traceback.
  - `nan` and `inf` are accepted and saved, so every later total prints `nan`.
  - Negative amounts and dates like `01.11.2026` are accepted. The bad date then never appears in any monthly report.
- **Check:** `python cli.py --file scratch.csv add --date x --category food --amount nan`, then `total`.
- **L3 / I2**

**C-03 `split_evenly` edge cases** (confident)
- **Where:** `ExpenseBook.split_evenly` and `cmd_split`.
- **What can go wrong:** `--people 0` raises ZeroDivisionError, and a negative number gives a negative share. The result is also unrounded, for example 1666.6666666666667, which is not a payable amount.
- **Check:** `python cli.py --file sample.csv split --people 0`, then `--people 3`.
- **L2 / I1**

**C-04 Float used for money** (confident on the behaviour, unverified on practical size)
- **Where:** `Expense.amount` and `total()`.
- **What can go wrong:** Summing floats drifts, and the CLI prints raw floats (`cmd_total`, `cmd_by_category`) while the reports use `:.2f`. The two outputs can then disagree. With mostly whole tenge the effect is small, but your sample already has 800.50.
- **Check:** Add 0.1 and 0.2 to a scratch file and run `total`, or run `python -c "print(0.1+0.2)"`.
- **L2 / I1**

**C-05 `load_csv` is fragile, and missing-file handling is inconsistent** (confident)
- **Where:** `storage.load_csv` and the `cmd_*` functions in `cli.py`.
- **What can go wrong:**
  - `date, category, amount, note = row` fails on a blank line or a row with the wrong number of columns, for example after hand-editing the file.
  - `add` uses `load_or_empty`, but every other command calls `load_csv` directly. On a first run, `list` therefore crashes with FileNotFoundError.
  - Until the file is fixed by hand, the tool is unusable.
- **Check:** Run `python cli.py list` in an empty folder. Then add a blank line in the middle of a copy of `sample.csv` and run `total`.
- **L2 / I2**

**C-06 Non-atomic save can wipe the whole history** (confident from reading, hard to trigger on demand)
- **Where:** `storage.save_csv`, called from `cmd_add` as load, then add, then save.
- **What can go wrong:** `open(path, "w")` truncates the file immediately, and rows are then written one by one with no temp file and no `with`. An interruption such as Ctrl-C, a full disk, or an encoding error (see D-01) leaves a truncated file. Two `add` runs at the same time also lose one update. There is no backup.
- **Check:** Read `save_csv` to confirm the truncate-then-write order. For a live demo, use D-01(a) on a copy.
- **L1 / I3**

## Maintainability

**M-01 Duplicated code and format knowledge** (confident)
- **Where:** `save_csv` and `report.export_csv` have identical bodies. The format names (`text`, `txt`, `monthly`, `csv`) appear in both `report.export` and `cli.cmd_export`. Five `open()` / `close()` pairs have no `with`.
- **What can go wrong:** Adding a column or a new format in one place silently skips the other. For example, a new `json` format would make `cmd_export` print "wrote None" when `--out` is missing. An exception between `open` and `close` leaks the handle.
- **Check:** `grep -n "txt" *.py`, and diff the two CSV-writing functions.
- **L2 / I1**

**M-02 Test gaps and README drift** (confident)
- **Where:** `tests/test_expenses.py` and `README.md`.
- **What can go wrong:** The tests cover only happy paths. Nothing covers `cli.py`, `split_evenly`, partial months, bad rows or validation, so C-01 to C-05 all pass the suite. The README says `python main.py ...`, but no `main.py` is in what you pasted, so the entry point looks like `cli.py`. `split` is not documented.
- **Check:** Run `python -m unittest discover -v`, then run the commands from C-01 and C-03. Also try `python main.py list`.
- **L3 / I1**

## Security

**S-01 CSV/formula injection** (unverified, depends on the spreadsheet app)
- **Where:** `note` and `category` are written raw by `save_csv` and `export_csv`.
- **What can go wrong:** A value starting with `=`, `+`, `-` or `@` may be treated as a formula when the CSV is opened in Excel or Sheets. This is low risk for a personal tool, but it matters if the data ever comes from other people.
- **Check:** Add `--note '=1+1'`, export to CSV, and open the file in your spreadsheet app.
- **L1 / I1**

**S-02 Output path can overwrite the data file** (confident)
- **Where:** `--out` and `--file` in `cmd_export` and `report.export_text`.
- **What can go wrong:** Nothing checks that the two paths differ or that the target is safe to overwrite. `export --format text --out expenses.csv` replaces your data with a text report, with no prompt. Any writable path is overwritten the same way, which only matters if args ever come from scripts or untrusted input.
- **Check:** On a copy, run `python cli.py --file copy.csv export --out copy.csv`, then look at the file.
- **L1 / I3**

## Dependency

**D-01 Platform-dependent defaults** (unverified, I haven't run it on Windows)
- **Where:** Every `open()` call in `storage.py` and `report.py`.
- **What can go wrong:**
  - There is no `encoding=`, so the locale default is used. Kazakh letters such as ә ғ қ ң ө ұ ү һ are not in cp1251, so on such a system a note could raise UnicodeEncodeError during save. By then the file is already truncated (C-06).
  - There is no `newline=""`, which the csv docs require. On Windows this may write `\r\r\n` and read back as blank lines, which triggers C-05.
  - If your tests already pass on Windows, the newline issue is probably not happening there.
- **Check:** Run `python -c "import locale; print(locale.getpreferredencoding())"`. Then add two entries to a scratch file and run `list`. Finally try `--note "қала"` on a scratch file.
- **L2 / I3**

**D-02 Python version claim not enforced** (unverified)
- **Where:** The README says "3.10 or newer".
- **What can go wrong:** I see nothing in the code that needs 3.10, since dataclasses need 3.7 and f-strings 3.6. There is no `pyproject.toml`, `.python-version`, CI or runtime check, so the real minimum and the behaviour on newer versions are unknown. There are no third-party packages, so there is no supply-chain risk to speak of.
- **Check:** Run `python --version`, then run the tests under any other installed Python.
- **L1 / I1**

## Agent operations

**A-01 Default data file is real, and git can't undo changes to it** (confident)
- **Where:** `DEFAULT_FILE = "expenses.csv"` in `cli.py`, and `expenses.csv` in `.gitignore`.
- **What can go wrong:** Any run without `--file` (a person, or an AI agent "just trying the CLI") reads and rewrites your real data. Git ignores that file, so `git diff` and `git checkout` cannot show or undo the change. Running from another folder also silently creates a second `expenses.csv`.
- **Check:** `git check-ignore -v expenses.csv`, then run `add` and confirm `git status` shows nothing.
- **L2 / I3**

**A-02 Retries create duplicates, and output is hard to parse** (confident)
- **Where:** `cmd_add`, `cmd_list`, and the error handling in `main`.
- **What can go wrong:** Entries have no ID and there is no dry-run, so a retried `add` (a timeout, a double-run) inserts a duplicate row. `list` prints space-joined text, so notes with spaces are ambiguous, and there is no `--json`. Errors come out as Python tracebacks, so a script or agent can't reliably tell what happened.
- **Check:** Run the same `add` twice on a scratch file and run `list`. Then check the exit code of a failing command with `echo $?` (or `%errorlevel%` on Windows).
- **L2 / I2**

## Would a design pattern help?

Mostly not. The big risks are validation, atomic saving, money as float, and test gaps, and no pattern fixes those. The one real fit is Strategy for exporters. `report.export` is an if/elif chain, and `cmd_export` repeats the same format names (M-01). A plain dict like `{"text": export_text, "csv": export_csv, ...}` gives you that Strategy idea in a few lines. A class hierarchy for three tiny functions would be over-engineering at this size. Adapter or Repository isn't needed, because `storage.py` is already the boundary, and it only pays off if you swap CSV for something like SQLite. If your assignment requires naming a pattern, Strategy for exporters is the honest choice, with the caveat that it only fixes M-01.

If you're short on time, run these checks first: C-01, C-02, C-03, A-01, and D-01 if you're on Windows.