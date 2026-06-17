"""
agents/supervisor.py
Supervisor Agent — the "manager" that orchestrates the full pipeline.
It reads the raw CSV, dispatches to all specialist agents in order,
then hands everything to the Report Agent for final synthesis.

Updated Flow:
  CSV input
     └─> Expense Agent   (categorise and summarise spending)
     └─> Budget Agent    (compare actual vs recommended budget)
     └─> Savings Agent   (identify savings opportunities)
     └─> Forecast Agent  (predict next month's spending)   ← NEW
     └─> Alert Agent     (flag anomalies & budget breaches) ← NEW
          └─> Report Agent (synthesise everything into one report)

The Supervisor is the only file that knows the full agent order.
Each individual agent only knows its own job.
"""

from tools.csv_parser import (
    parse_transactions,
    split_income_expenses,
    total_income,
    total_expenses,
)
from agents.expense_agent  import run_expense_agent
from agents.budget_agent   import run_budget_agent
from agents.savings_agent  import run_savings_agent
from agents.forecast_agent import run_forecast_agent   # NEW
from agents.alert_agent    import run_alert_agent       # NEW
from agents.report_agent   import run_report_agent


def run_supervisor(csv_content: str) -> dict:
    """
    Entry point for the whole pipeline.
    Takes raw CSV text, runs all agents in sequence, returns full results dict.
    """

    # ── Parse CSV into structured transaction lists ──────────────────────────
    print("[Supervisor] Parsing transactions...")
    transactions = parse_transactions(csv_content)
    income_txns, expense_txns = split_income_expenses(transactions)

    inc  = total_income(income_txns)
    exps = total_expenses(expense_txns)
    print(f"[Supervisor] Found {len(transactions)} transactions | "
          f"Income: ${inc} | Expenses: ${exps}")

    # ── Step 1: Expense Agent ────────────────────────────────────────────────
    # Categorises every expense and identifies top merchants/categories
    print("[Supervisor] → Dispatching to Expense Agent...")
    expense_result = run_expense_agent(expense_txns)

    # ── Step 2: Budget Agent ─────────────────────────────────────────────────
    # Compares actual category spend against recommended budget limits
    print("[Supervisor] → Dispatching to Budget Agent...")
    budget_result = run_budget_agent(expense_result, inc)

    # ── Step 3: Savings Agent ────────────────────────────────────────────────
    # Scans for recurring costs and suggests where to cut back
    print("[Supervisor] → Dispatching to Savings Agent...")
    savings_result = run_savings_agent(expense_txns, inc)

    # ── Step 4: Forecast Agent (NEW) ─────────────────────────────────────────
    # Forward-looking: predicts next month's spend by category
    print("[Supervisor] → Dispatching to Forecast Agent...")
    forecast_result = run_forecast_agent(expense_txns, expense_result)

    # ── Step 5: Alert Agent (NEW) ────────────────────────────────────────────
    # Compliance layer: flags anomalous charges and budget breaches
    print("[Supervisor] → Dispatching to Alert Agent...")
    alert_result = run_alert_agent(expense_txns, budget_result)

    # ── Step 6: Report Agent (final aggregator) ──────────────────────────────
    # Pulls all agent outputs together into one human-readable report
    print("[Supervisor] → Dispatching to Report Agent (final synthesis)...")
    report_result = run_report_agent(
        expense_result,
        budget_result,
        savings_result,
        forecast_result,   # NEW
        alert_result,      # NEW
    )

    print("[Supervisor] ✓ Pipeline complete.")

    # Return all results so the dashboard and API can access any layer
    return {
        "expense_analysis":  expense_result,
        "budget_analysis":   budget_result,
        "savings_analysis":  savings_result,
        "forecast_analysis": forecast_result,   # NEW
        "alert_analysis":    alert_result,       # NEW
        "report":            report_result,
    }