M-02 Test gaps and README drift

$ python -m unittest discover -v
test_add_and_list (tests.test_expenses.ExpenseBookTests.test_add_and_list) ... ok
test_csv_roundtrip (tests.test_expenses.ExpenseBookTests.test_csv_roundtrip) ... ok
test_empty_book (tests.test_expenses.ExpenseBookTests.test_empty_book) ... ok
test_export_csv_writes_file (tests.test_expenses.ExpenseBookTests.test_export_csv_writes_file) ... ok
test_export_text_contains_total (tests.test_expenses.ExpenseBookTests.test_export_text_contains_total) ... ok
test_monthly_summary (tests.test_expenses.ExpenseBookTests.test_monthly_summary) ... ok
test_total (tests.test_expenses.ExpenseBookTests.test_total) ... ok
test_totals_by_category (tests.test_expenses.ExpenseBookTests.test_totals_by_category) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.003s

OK
exit code: 0

$ python main.py list
python: can't open file '/workspace/sis5/repo/main.py': [Errno 2] No such file or directory
exit code: 2

$ ls main.py
ls: cannot access 'main.py': No such file or directory

README first lines:
     1	# Expense calculator
     2	
     3	A small command line tool to keep track of personal expenses in KZT.
     4	
     5	## How to run
     6	
     7	Python 3.10 or newer is required.
     8	
     9	    python main.py add --date 2026-11-01 --category food --amount 1200 --note coffee
    10	    python main.py list
    11	    python main.py total
    12	    python main.py by-category
    13	    python main.py monthly --month 2026-11
    14	    python main.py export --format text --out report.txt
    15	
    16	The default data file is `expenses.csv` in the current folder.
    17	
    18	Dates should be written as YYYY-MM-DD. Amounts are in KZT.
    19	
    20	## Tests
    21	
    22	    python -m unittest discover -v

Does test file mention cli, split_evenly, nan, blank, validation?
(no matches)

split is not in the README:
(no 'split' in README.md)
