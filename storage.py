"""Load and save expenses as a simple CSV file."""

import csv

from expenses import ExpenseBook


def load_csv(path):
    book = ExpenseBook()
    with open(path, "r") as f:
        reader = csv.reader(f)
        first = True
        for row in reader:
            if not row:
                continue
            if first:
                first = False
                if row[0].lower() == "date":
                    continue
            if len(row) != 4:
                raise ValueError(f"{path}, line {reader.line_num}: expected 4 columns, got {len(row)}")
            date, category, amount, note = row
            try:
                book.add(date, category, amount, note)
            except ValueError as error:
                raise ValueError(f"{path}, line {reader.line_num}: {error}") from error
    return book


def save_csv(path, book):
    f = open(path, "w")
    writer = csv.writer(f)
    writer.writerow(["date", "category", "amount", "note"])
    for expense in book.list_all():
        writer.writerow([expense.date, expense.category, expense.amount, expense.note])
    f.close()
