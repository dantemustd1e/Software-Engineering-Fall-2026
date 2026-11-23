"""In-memory expense book. Amounts are stored in KZT."""

import math
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Expense:
    date: str
    category: str
    amount: float
    note: str = ""


class ExpenseBook:
    def __init__(self, items=None):
        if items is None:
            self.items = []
        else:
            self.items = list(items)

    def add(self, date, category, amount, note=""):
        date = str(date)
        try:
            if len(date) != 10:
                raise ValueError
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"invalid date {date!r}, expected YYYY-MM-DD") from None
        try:
            value = float(amount)
        except (TypeError, ValueError):
            raise ValueError(f"invalid amount {amount!r}, use a plain number like 800.50") from None
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"invalid amount {amount!r}, must be a finite number, 0 or more")
        expense = Expense(date, str(category), value, str(note))
        self.items.append(expense)
        return expense

    def list_all(self):
        return list(self.items)

    def total(self):
        value = 0.0
        for expense in self.items:
            value = value + expense.amount
        return value

    def totals_by_category(self):
        totals = {}
        for expense in self.items:
            if expense.category in totals:
                totals[expense.category] = totals[expense.category] + expense.amount
            else:
                totals[expense.category] = expense.amount
        return totals

    def monthly_summary(self, year_month):
        selected = []
        for expense in self.items:
            if expense.date.startswith(year_month):
                selected.append(expense)
        month_book = ExpenseBook(selected)
        return {
            "month": year_month,
            "count": len(selected),
            "total": month_book.total(),
            "by_category": month_book.totals_by_category(),
            "items": selected,
        }

    def split_evenly(self, n):
        return self.total() / n
