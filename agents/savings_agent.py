"""
agents/savings_agent.py
Savings Agent — scans all transactions to find savings opportunities,
like cutting subscriptions or reducing food delivery spend.
"""

import json
from typing import List, Dict, Any
from tools.finance_tools import ask_llm


def run_savings_agent(expenses: List[Dict], total_income: float) -> Dict[str, Any]:
    """
    Input : raw expense list, total income
    Output: actionable savings tips with estimated monthly/annual savings.
    """

    transaction_text = "\n".join(
        f"{t['description']} - ${t['amount']:.2f}" for t in expenses
    )

    system_prompt = """You are a personal savings advisor AI.
Analyse the user's transactions and identify realistic savings opportunities.
Focus on: recurring subscriptions, frequent food delivery, impulse purchases.

Respond ONLY with valid JSON — no markdown, no explanation.
Format:
{
  "savings_opportunities": [
    {
      "description": "Reduce Uber Eats by 50%",
      "monthly_savings": 90,
      "annual_savings": 1080
    }
  ],
  "total_monthly_savings": 118,
  "total_annual_savings": 1416,
  "current_savings_rate_pct": 28.0,
  "recommended_savings_rate_pct": 20.0
}"""

    user_prompt = f"""
Monthly Income: ${total_income:.2f}
Transactions:
{transaction_text}

Find practical ways this user can save money each month.
"""

    raw = ask_llm(system_prompt, user_prompt)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"raw_analysis": raw, "savings_opportunities": []}

    return result
