"""
agents/forecast_agent.py
Forecast Agent — forward-looking agent that analyzes spending patterns
and predicts next month's expenses by category.

This is what makes the system feel like a real fintech product:
instead of just reviewing what happened, it helps the user prepare
for what's coming next.

Flow:
  Takes expense transactions + category totals from expense_agent
      └─> LLM analyzes trends and spending velocity
            └─> Returns predicted next-month spending + risk flags
"""

import json
from typing import List, Dict, Any
from tools.finance_tools import ask_llm


def run_forecast_agent(expenses: List[Dict], expense_analysis: Dict) -> Dict[str, Any]:
    """
    Input : raw expense list + category breakdown from expense_agent
    Output: predicted next month's spend per category, risk categories,
            and an expected change percentage.
    """

    # Build a readable summary of current category spend for the LLM
    categories     = expense_analysis.get("categories", {})
    total_spending = sum(categories.values())
    category_text  = "\n".join(
        f"  {cat}: ${amt:.2f}" for cat, amt in categories.items()
    )

    # List individual transactions so the LLM can spot velocity/frequency
    transaction_text = "\n".join(
        f"  {t['date']} | {t['description']} | ${t['amount']:.2f}"
        for t in expenses
    )

    system_prompt = """You are a predictive financial analyst AI.
Based on the user's current month transactions and category totals,
forecast their likely spending for the next month.

Identify which categories are trending upward (risk categories).
Be realistic — base predictions on the data, not assumptions.

Respond ONLY with valid JSON — no markdown, no explanation.
Format:
{
  "predicted_spending": {
    "Food": 320.00,
    "Shopping": 110.00
  },
  "predicted_total": 2050.00,
  "highest_risk_category": "Food",
  "expected_change_pct": 8.5,
  "forecast_summary": "One sentence summary of the outlook."
}"""

    user_prompt = f"""
Current Month Category Totals:
{category_text}

Total This Month: ${total_spending:.2f}

Individual Transactions:
{transaction_text}

Forecast next month's spending based on these patterns.
"""

    raw = ask_llm(system_prompt, user_prompt)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # If JSON parsing fails, return raw text so pipeline doesn't crash
        result = {"raw_forecast": raw, "predicted_spending": {}}

    return result