"""Text and CSV reports for an expense book."""

import csv


def format_line(expense):
    return f"{expense.date}  {expense.category:12}  {expense.amount:10.2f}  {expense.note}"


def export_text(book, path=None):
    lines = ["Expense report", "-" * 40]
    for expense in book.list_all():
        lines.append(format_line(expense))
    lines.append("-" * 40)
    lines.append("Total: {:.2f}".format(book.total()))
    lines.append("")
    lines.append("By category:")
    totals = book.totals_by_category()
    for category in totals:
        lines.append(f"  {category}: {totals[category]:.2f}")
    text = "\n".join(lines) + "\n"
    if path:
        f = open(path, "w")
        f.write(text)
        f.close()
    return text


def export_csv(book, path):
    f = open(path, "w")
    writer = csv.writer(f)
    writer.writerow(["date", "category", "amount", "note"])
    for expense in book.list_all():
        writer.writerow([expense.date, expense.category, expense.amount, expense.note])
    f.close()


def export_monthly(book, month, path=None):
    summary = book.monthly_summary(month)
    lines = [f"Monthly report for {month}", "-" * 40]
    for expense in summary["items"]:
        lines.append(format_line(expense))
    lines.append("-" * 40)
    lines.append("Total: {:.2f}".format(summary["total"]))
    lines.append("Count: {}".format(summary["count"]))
    lines.append("By category:")
    for category in summary["by_category"]:
        lines.append(f"  {category}: {summary['by_category'][category]:.2f}")
    text = "\n".join(lines) + "\n"
    if path:
        f = open(path, "w")
        f.write(text)
        f.close()
    return text


def _export_csv(book, path, month):
    if not path:
        raise ValueError("csv export needs a path")
    export_csv(book, path)
    return path


def _export_monthly(book, path, month):
    if month is None:
        raise ValueError("monthly export needs a month")
    return export_monthly(book, month, path)


def _export_text(book, path, month):
    return export_text(book, path)


EXPORTERS = {
    "text": _export_text,
    "txt": _export_text,
    "csv": _export_csv,
    "monthly": _export_monthly,
}


def export(book, fmt, path=None, month=None):
    try:
        exporter = EXPORTERS[fmt]
    except KeyError:
        raise ValueError("unknown format: " + str(fmt)) from None
    return exporter(book, path, month)
