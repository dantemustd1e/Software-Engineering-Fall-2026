"""Load and save expenses as a simple CSV file."""

import csv

from expenses import ExpenseBook


def load_csv(path):
    book = ExpenseBook()
    f = open(path, "r")
    reader = csv.reader(f)
    first = True
    for row in reader:
        if first:
            first = False
            if row and row[0].lower() == "date":
                continue
        date, category, amount, note = row
        book.add(date, category, amount, note)
    f.close()
    return book


def save_csv(path, book):
    f = open(path, "w")
    writer = csv.writer(f)
    writer.writerow(["date", "category", "amount", "note"])
    for expense in book.list_all():
        writer.writerow([expense.date, expense.category, expense.amount, expense.note])
    f.close()
