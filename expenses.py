"""In-memory expense book. Amounts are stored in KZT."""

from dataclasses import dataclass


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
        expense = Expense(str(date), str(category), float(amount), str(note))
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
