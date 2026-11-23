I haven't touched any files and haven't run any of this. The hunk headers are hand-counted from your paste, so run `git apply --check` first, or apply by hand if it complains. I used 1-line context in `cli.py` to keep the hunks short.

## Decisions I made (change any of them)

- **Decimal comma:** `800,50` is rejected with a clear message, not accepted. `1,200` would otherwise silently become 1.2.
- **Validation location:** it lives in `ExpenseBook.add`, as you specified. `load_csv` also calls `add`, so an existing CSV with negative amounts or odd dates will now fail to load, with its line number in the message.
- **Missing file:** read commands treat a missing file as an empty book, like `add` does. The downside is that a typo in `--file` shows a total of 0 instead of an error.
- **Error output:** `main()` catches `ValueError` and prints one line to stderr with exit code 1. The downside is that a real bug that raises `ValueError` also loses its traceback.
- **Extra test:** you asked for one test per item. Your AGENTS rule ("new error means new test") needs a third small CLI test, so I added it. It is marked below, and you can drop it if you want strictly one per item.

## (a) C-02: validation

```diff
--- a/expenses.py
+++ b/expenses.py
@@ -1,6 +1,8 @@
 """In-memory expense book. Amounts are stored in KZT."""
 
 from dataclasses import dataclass
+from datetime import datetime
+import math
 
 
 @dataclass
@@ -18,8 +20,21 @@ class ExpenseBook:
         else:
             self.items = list(items)
 
     def add(self, date, category, amount, note=""):
-        expense = Expense(str(date), str(category), float(amount), str(note))
+        date = str(date)
+        try:
+            if len(date) != 10:
+                raise ValueError
+            datetime.strptime(date, "%Y-%m-%d")
+        except ValueError:
+            raise ValueError(f"invalid date {date!r}, expected YYYY-MM-DD") from None
+        try:
+            value = float(amount)
+        except (TypeError, ValueError):
+            raise ValueError(f"invalid amount {amount!r}, use a plain number like 800.50") from None
+        if not math.isfinite(value) or value < 0:
+            raise ValueError(f"invalid amount {amount!r}, must be a finite number, 0 or more")
+        expense = Expense(date, str(category), value, str(note))
         self.items.append(expense)
         return expense
```

The `len(date) != 10` check is there because `strptime` alone accepts `2026-1-5`, which `monthly` would never match.

```diff
--- a/cli.py
+++ b/cli.py
@@ -110,3 +110,7 @@ def main(argv=None):
         return 1
-    args.func(args)
+    try:
+        args.func(args)
+    except ValueError as error:
+        print("error:", error, file=sys.stderr)
+        return 1
     return 0
```

For `add`, validation happens before `save_csv`, so a bad input never touches the file.

## (b) C-05: loading

```diff
--- a/storage.py
+++ b/storage.py
@@ -7,17 +7,23 @@
 
 def load_csv(path):
     book = ExpenseBook()
-    f = open(path, "r")
-    reader = csv.reader(f)
-    first = True
-    for row in reader:
-        if first:
-            first = False
-            if row and row[0].lower() == "date":
-                continue
-        date, category, amount, note = row
-        book.add(date, category, amount, note)
-    f.close()
+    with open(path, "r") as f:
+        reader = csv.reader(f)
+        first = True
+        for row in reader:
+            if not row:
+                continue
+            if first:
+                first = False
+                if row[0].lower() == "date":
+                    continue
+            if len(row) != 4:
+                raise ValueError(f"{path}, line {reader.line_num}: expected 4 columns, got {len(row)}")
+            date, category, amount, note = row
+            try:
+                book.add(date, category, amount, note)
+            except ValueError as error:
+                raise ValueError(f"{path}, line {reader.line_num}: {error}") from error
     return book
 
 
```

I switched to `with` because the function can now raise partway through, and the old `f.close()` would be skipped. I did not add `encoding=` or `newline=""`, because that is D-01 and out of scope.

```diff
--- a/cli.py
+++ b/cli.py
@@ -27,3 +27,3 @@
 def cmd_list(args):
-    book = load_csv(args.file)
+    book = load_or_empty(args.file)
     for expense in book.list_all():
@@ -34,3 +34,3 @@
 def cmd_total(args):
-    book = load_csv(args.file)
+    book = load_or_empty(args.file)
     print(book.total())
@@ -39,3 +39,3 @@
 def cmd_by_category(args):
-    book = load_csv(args.file)
+    book = load_or_empty(args.file)
     totals = book.totals_by_category()
@@ -46,3 +46,3 @@
 def cmd_monthly(args):
-    book = load_csv(args.file)
+    book = load_or_empty(args.file)
     summary = book.monthly_summary(args.month)
@@ -56,3 +56,3 @@
 def cmd_export(args):
-    book = load_csv(args.file)
+    book = load_or_empty(args.file)
     out = report.export(book, args.format, path=args.out, month=args.month)
@@ -68,3 +68,3 @@
 def cmd_split(args):
-    book = load_csv(args.file)
+    book = load_or_empty(args.file)
     print("each person pays:", book.split_evenly(args.people))
```

## Tests for (a) and (b)

All of it goes in `tests/test_expenses.py`, as one diff so the line numbers stay valid:

- **A** (`test_add_rejects_invalid_input`) is the requested test for (a).
- **B** (`test_load_csv_skips_blank_lines_and_rejects_short_rows`) is the requested test for (b).
- **C** (`CliTests`) is the extra test, covering the missing file and the clean error exit.

```diff
--- a/tests/test_expenses.py
+++ b/tests/test_expenses.py
@@ -3,7 +3,10 @@
+import contextlib
+import io
 import os
 import tempfile
 import unittest
 
 from expenses import ExpenseBook
 from storage import load_csv, save_csv
+import cli
 import report
@@ -75,6 +78,53 @@ class ExpenseBookTests(unittest.TestCase):
             self.assertIn("bus", content)
         finally:
             os.remove(path)
+
+    def test_add_rejects_invalid_input(self):
+        book = ExpenseBook()
+        for date, amount in [
+            ("2026-11-01", "nan"),
+            ("2026-11-01", "inf"),
+            ("2026-11-01", "-5"),
+            ("2026-11-01", "800,50"),
+            ("01.11.2026", "100"),
+            ("2026-1-5", "100"),
+            ("2026-13-01", "100"),
+        ]:
+            with self.subTest(date=date, amount=amount):
+                with self.assertRaises(ValueError):
+                    book.add(date, "food", amount)
+        self.assertEqual(book.list_all(), [])
+        book.add("2026-11-02", "food", "800.50")
+        self.assertEqual(book.list_all()[0].amount, 800.5)
+
+    def test_load_csv_skips_blank_lines_and_rejects_short_rows(self):
+        with tempfile.TemporaryDirectory() as folder:
+            good = os.path.join(folder, "good.csv")
+            with open(good, "w") as handle:
+                handle.write("date,category,amount,note\n\n2026-11-01,food,1200,coffee\n\n")
+            self.assertEqual(len(load_csv(good).list_all()), 1)
+
+            short = os.path.join(folder, "short.csv")
+            with open(short, "w") as handle:
+                handle.write("date,category,amount,note\n2026-11-01,food,1200\n")
+            with self.assertRaises(ValueError) as caught:
+                load_csv(short)
+            self.assertIn("line 2", str(caught.exception))
 
 
+class CliTests(unittest.TestCase):
+    def test_missing_file_and_bad_amount(self):
+        with tempfile.TemporaryDirectory() as folder:
+            path = os.path.join(folder, "scratch.csv")
+            out, err = io.StringIO(), io.StringIO()
+            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
+                listed = cli.main(["--file", path, "list"])
+                added = cli.main(["--file", path, "add", "--date", "2026-11-01",
+                                  "--category", "food", "--amount", "800,50"])
+            self.assertEqual(listed, 0)
+            self.assertEqual(added, 1)
+            self.assertIn("invalid amount", err.getvalue())
+            self.assertFalse(os.path.exists(path))
+
+
 if __name__ == "__main__":
     unittest.main()
```

The existing tests and `sample.csv` should still pass, because their dates and amounts are all valid under the new rules.

## (c) Dict dispatch for export

My view is that it is worth doing, but only modestly. The three exporters have different signatures, so the dict needs three tiny adapters, and `report.py` ends up about the same length. The real gain is in `cli.py`: `cmd_export` currently hard-codes the format names (`text`, `txt`, `monthly`). Once `report.export` owns the dispatch, `cmd_export` only needs to check whether `--out` was given. That is exactly equivalent to the old behaviour: csv without `--out` and unknown formats raise before the print. If you'd rather keep the if/elif, keep only the `cli.py` hunk below and skip the `report.py` change.

```diff
--- a/report.py
+++ b/report.py
@@ -54,17 +54,34 @@ def export_monthly(book, month, path=None):
     return text
 
 
-def export(book, fmt, path=None, month=None):
-    if fmt == "text" or fmt == "txt":
-        return export_text(book, path)
-    elif fmt == "csv":
-        if not path:
-            raise ValueError("csv export needs a path")
-        export_csv(book, path)
-        return path
-    elif fmt == "monthly":
-        if month is None:
-            raise ValueError("monthly export needs a month")
-        return export_monthly(book, month, path)
-    else:
-        raise ValueError("unknown format: " + str(fmt))
+def _export_csv(book, path, month):
+    if not path:
+        raise ValueError("csv export needs a path")
+    export_csv(book, path)
+    return path
+
+
+def _export_monthly(book, path, month):
+    if month is None:
+        raise ValueError("monthly export needs a month")
+    return export_monthly(book, month, path)
+
+
+def _export_text(book, path, month):
+    return export_text(book, path)
+
+
+EXPORTERS = {
+    "text": _export_text,
+    "txt": _export_text,
+    "csv": _export_csv,
+    "monthly": _export_monthly,
+}
+
+
+def export(book, fmt, path=None, month=None):
+    try:
+        exporter = EXPORTERS[fmt]
+    except KeyError:
+        raise ValueError("unknown format: " + str(fmt)) from None
+    return exporter(book, path, month)
```

```diff
--- a/cli.py
+++ b/cli.py
@@ -58,9 +58,6 @@
     out = report.export(book, args.format, path=args.out, month=args.month)
-    if args.format == "text" or args.format == "txt" or args.format == "monthly":
-        if args.out:
-            print("wrote", args.out)
-        else:
-            print(out, end="")
-    else:
-        print("wrote", args.out)
+    if args.out:
+        print("wrote", args.out)
+    else:
+        print(out, end="")
 
```

Your rules don't require a test for (c), since it adds no new error. The suite does not currently reach the `txt`, `monthly` or unknown-format paths through `export()`, so I'd add this to `ExpenseBookTests`:

```python
    def test_export_dispatch(self):
        self.assertEqual(report.export(self.book, "txt"), report.export(self.book, "text"))
        self.assertIn("Monthly report for 2026-11", report.export(self.book, "monthly", month="2026-11"))
        with self.assertRaises(ValueError):
            report.export(self.book, "monthly")
        with self.assertRaises(ValueError):
            report.export(self.book, "pdf")
```

## How to check (scratch file only)

```
python -m unittest discover -v
python cli.py --file scratch.csv list                       # empty book, exit 0, no file created
python cli.py --file scratch.csv add --date 2026-11-01 --category food --amount 800,50   # one error line, exit 1
python cli.py --file scratch.csv add --date 2026-11-01 --category food --amount 800.50
printf 'date,category,amount,note\n\n2026-11-01,food\n' > bad.csv
python cli.py --file bad.csv total                          # "bad.csv, line 3: expected 4 columns, got 2"
```

Before the first run against your real `expenses.csv`, copy it and run `total` on the copy. If it contains negative amounts or old-style dates, it will now stop at that line.

Not touched: C-03 (`split_evenly` with 0 people), C-06 (non-atomic save) and D-01 (encoding and newline).