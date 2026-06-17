"""
agents/budget_agent.py
Budget Agent — compares actual spending against recommended budget limits
and flags any categories where the user overspent.
"""

import json
from typing import Dict, Any
from tools.finance_tools import ask_llm
from core.config import DEFAULT_BUDGET


def run_budget_agent(expense_analysis: Dict, total_income: float) -> Dict[str, Any]:
    """
    Input : expense_analysis (output of expense_agent), total monthly income
    Output: dict with recommended budget, actual vs recommended comparison,
            and overspending alerts.
    """

    actual_categories = expense_analysis.get("categories", {})
    total_expenses    = sum(actual_categories.values())

    system_prompt = """You are a personal finance advisor AI.
Given a user's income, actual spending by category, and a default budget template,
produce a practical monthly budget and overspending analysis.

Respond ONLY with valid JSON — no markdown, no explanation.
Format:
{
  "recommended_budget": {"Housing": 800, "Food": 300, ...},
  "overspending": [
    {"category": "Food", "recommended": 300, "actual": 450, "overspent_by": 150}
  ],
  "remaining_balance": 700,
  "budget_summary": "One sentence summary."
}"""

    user_prompt = f"""
Monthly Income    : ${total_income:.2f}
Total Expenses    : ${total_expenses:.2f}
Actual Spending   : {json.dumps(actual_categories)}
Default Budget    : {json.dumps(DEFAULT_BUDGET)}

Compare actual vs default, adjust the recommended budget to this user's income,
and flag any category where actual > recommended.
"""

    raw = ask_llm(system_prompt, user_prompt)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"raw_analysis": raw}

    # Store totals for the report agent
    result["total_income"]   = total_income
    result["total_expenses"] = total_expenses
    return result
