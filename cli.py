"""Command line entry point for the expense calculator."""

import argparse
import os
import sys

from expenses import ExpenseBook
from storage import load_csv, save_csv
import report

DEFAULT_FILE = "expenses.csv"


def load_or_empty(path):
    if os.path.exists(path):
        return load_csv(path)
    return ExpenseBook()


def cmd_add(args):
    book = load_or_empty(args.file)
    book.add(args.date, args.category, args.amount, args.note)
    save_csv(args.file, book)
    print("added:", args.date, args.category, args.amount, args.note)


def cmd_list(args):
    book = load_csv(args.file)
    for expense in book.list_all():
        print(expense.date, expense.category, expense.amount, expense.note)
    print("total:", book.total())


def cmd_total(args):
    book = load_csv(args.file)
    print(book.total())


def cmd_by_category(args):
    book = load_csv(args.file)
    totals = book.totals_by_category()
    for category in totals:
        print(f"{category}: {totals[category]}")


def cmd_monthly(args):
    book = load_csv(args.file)
    summary = book.monthly_summary(args.month)
    print("month:", summary["month"])
    print("count:", summary["count"])
    print("total:", summary["total"])
    for category in summary["by_category"]:
        print(f"  {category}: {summary['by_category'][category]}")


def cmd_export(args):
    book = load_csv(args.file)
    out = report.export(book, args.format, path=args.out, month=args.month)
    if args.out:
        print("wrote", args.out)
    else:
        print(out, end="")


def cmd_split(args):
    book = load_csv(args.file)
    print("each person pays:", book.split_evenly(args.people))


def build_parser():
    parser = argparse.ArgumentParser(description="Simple expense calculator")
    parser.add_argument("--file", default=DEFAULT_FILE, help="csv file with expenses")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add")
    add_p.add_argument("--date", required=True)
    add_p.add_argument("--category", required=True)
    add_p.add_argument("--amount", required=True)
    add_p.add_argument("--note", default="")
    add_p.set_defaults(func=cmd_add)

    sub.add_parser("list").set_defaults(func=cmd_list)
    sub.add_parser("total").set_defaults(func=cmd_total)
    sub.add_parser("by-category").set_defaults(func=cmd_by_category)

    mon_p = sub.add_parser("monthly")
    mon_p.add_argument("--month", required=True, help="YYYY-MM")
    mon_p.set_defaults(func=cmd_monthly)

    exp_p = sub.add_parser("export")
    exp_p.add_argument("--format", default="text")
    exp_p.add_argument("--out", default=None)
    exp_p.add_argument("--month", default=None)
    exp_p.set_defaults(func=cmd_export)

    split_p = sub.add_parser("split")
    split_p.add_argument("--people", type=int, required=True)
    split_p.set_defaults(func=cmd_split)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
