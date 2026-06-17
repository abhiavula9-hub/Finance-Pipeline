"""
agents/supervisor.py
Supervisor Agent — the "manager" that orchestrates the full pipeline.
It reads the raw CSV, dispatches to the three specialist agents in order,
then hands everything to the Report Agent.

Flow:
  CSV input
     └─> Expense Agent  (categorise spending)
     └─> Budget Agent   (compare vs budget)
     └─> Savings Agent  (find savings opportunities)
          └─> Report Agent (synthesise final report)
"""

from tools.csv_parser import (
    parse_transactions,
    split_income_expenses,
    total_income,
    total_expenses,
)
from agents.expense_agent import run_expense_agent
from agents.budget_agent   import run_budget_agent
from agents.savings_agent  import run_savings_agent
from agents.report_agent   import run_report_agent


def run_supervisor(csv_content: str) -> dict:
    """
    Entry point for the whole pipeline.
    Takes raw CSV text, returns the full analysis dict.
    """

    print("[Supervisor] Parsing transactions...")
    transactions = parse_transactions(csv_content)
    income_txns, expense_txns = split_income_expenses(transactions)

    inc  = total_income(income_txns)
    exps = total_expenses(expense_txns)
    print(f"[Supervisor] Found {len(transactions)} transactions | "
          f"Income: ${inc} | Expenses: ${exps}")

    # ── Step 1: Expense Agent ────────────────────────────────────────────────
    print("[Supervisor] → Dispatching to Expense Agent...")
    expense_result = run_expense_agent(expense_txns)

    # ── Step 2: Budget Agent ─────────────────────────────────────────────────
    print("[Supervisor] → Dispatching to Budget Agent...")
    budget_result = run_budget_agent(expense_result, inc)

    # ── Step 3: Savings Agent ────────────────────────────────────────────────
    print("[Supervisor] → Dispatching to Savings Agent...")
    savings_result = run_savings_agent(expense_txns, inc)

    # ── Step 4: Report Agent (aggregator) ───────────────────────────────────
    print("[Supervisor] → Dispatching to Report Agent (final synthesis)...")
    report_result = run_report_agent(expense_result, budget_result, savings_result)

    print("[Supervisor] ✓ Pipeline complete.")

    # Return everything so the dashboard and API can pick what they need
    return {
        "expense_analysis": expense_result,
        "budget_analysis":  budget_result,
        "savings_analysis": savings_result,
        "report":           report_result,
    }
