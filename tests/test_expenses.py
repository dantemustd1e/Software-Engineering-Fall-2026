"""Basic tests for the expense calculator."""

import os
import tempfile
import unittest

from expenses import ExpenseBook
from storage import load_csv, save_csv
import report


class ExpenseBookTests(unittest.TestCase):
    def setUp(self):
        self.book = ExpenseBook()
        self.book.add("2026-11-01", "food", 1200, "coffee")
        self.book.add("2026-11-01", "food", 3500, "lunch at canteen")
        self.book.add("2026-11-03", "transport", 300, "bus")
        self.book.add("2026-10-20", "study", 4500, "printouts")

    def test_add_and_list(self):
        items = self.book.list_all()
        self.assertEqual(len(items), 4)
        self.assertEqual(items[0].date, "2026-11-01")
        self.assertEqual(items[0].category, "food")
        self.assertEqual(items[0].amount, 1200)
        self.assertEqual(items[0].note, "coffee")

    def test_total(self):
        self.assertEqual(self.book.total(), 1200 + 3500 + 300 + 4500)

    def test_totals_by_category(self):
        totals = self.book.totals_by_category()
        self.assertEqual(totals["food"], 4700)
        self.assertEqual(totals["transport"], 300)
        self.assertEqual(totals["study"], 4500)

    def test_monthly_summary(self):
        november = self.book.monthly_summary("2026-11")
        self.assertEqual(november["count"], 3)
        self.assertEqual(november["total"], 5000)
        self.assertEqual(november["by_category"]["food"], 4700)

    def test_empty_book(self):
        empty = ExpenseBook()
        self.assertEqual(empty.list_all(), [])
        self.assertEqual(empty.total(), 0)
        self.assertEqual(empty.totals_by_category(), {})

    def test_csv_roundtrip(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            save_csv(path, self.book)
            loaded = load_csv(path)
            self.assertEqual(len(loaded.list_all()), 4)
            self.assertEqual(loaded.total(), self.book.total())
            self.assertEqual(loaded.list_all()[1].note, "lunch at canteen")
        finally:
            os.remove(path)

    def test_export_text_contains_total(self):
        text = report.export_text(self.book)
        self.assertIn("Expense report", text)
        self.assertIn("Total:", text)
        self.assertIn("coffee", text)

    def test_export_csv_writes_file(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            report.export(self.book, "csv", path=path)
            with open(path) as handle:
                content = handle.read()
            self.assertIn("date,category,amount,note", content)
            self.assertIn("bus", content)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
