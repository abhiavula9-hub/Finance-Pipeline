"""
tools/csv_parser.py
Reads the uploaded transactions CSV and returns structured data.
All agents call these helpers instead of touching raw files themselves.
"""

import csv
import io
from typing import List, Dict, Any


def parse_transactions(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parse CSV text into a list of transaction dicts.
    Handles both positive (income) and negative (expense) amounts.

    Expected columns: Date, Description, Amount
    Returns: [{"date": str, "description": str, "amount": float}, ...]
    """
    transactions = []
    reader = csv.DictReader(io.StringIO(csv_content.strip()))

    for row in reader:
        try:
            amount = float(str(row.get("Amount", "0")).replace(",", ""))
            transactions.append({
                "date":        row.get("Date", "").strip(),
                "description": row.get("Description", "").strip(),
                "amount":      amount,
            })
        except ValueError:
            # Skip rows with unparseable amounts (e.g. header repeats)
            continue

    return transactions


def split_income_expenses(transactions: List[Dict]) -> tuple:
    """
    Separate transactions into income (positive) and expenses (negative).
    Returns (income_list, expense_list) — amounts in expense_list are positive.
    """
    income   = [t for t in transactions if t["amount"] > 0]
    expenses = [t for t in transactions if t["amount"] < 0]

    # Make expense amounts positive for easier maths downstream
    for e in expenses:
        e["amount"] = abs(e["amount"])

    return income, expenses


def total_income(income_list: List[Dict]) -> float:
    """Sum all income transactions."""
    return round(sum(t["amount"] for t in income_list), 2)


def total_expenses(expense_list: List[Dict]) -> float:
    """Sum all expense transactions (already made positive)."""
    return round(sum(t["amount"] for t in expense_list), 2)
