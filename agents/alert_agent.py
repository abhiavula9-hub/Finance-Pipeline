"""
agents/alert_agent.py
Alert Agent — scans transactions for anomalies and budget breaches.

This is the compliance / oversight layer of the system.
In a real corporate fintech product, this is what would trigger
notifications to a finance team or flag suspicious activity.

Two types of alerts it generates:
  1. Anomaly Alert  — a charge that's unusually high vs. typical spend
                      at the same merchant (e.g. Uber Eats $20 → $120)
  2. Budget Alert   — a category where actual spending exceeds the
                      recommended limit (e.g. Entertainment $200 → $250)

Flow:
  Takes raw expenses + budget analysis output
      └─> LLM cross-references merchant patterns and category limits
            └─> Returns structured list of alerts with severity levels
"""

import json
from typing import List, Dict, Any
from tools.finance_tools import ask_llm


def run_alert_agent(expenses: List[Dict], budget_analysis: Dict) -> Dict[str, Any]:
    """
    Input : raw expense list + budget_analysis (from budget_agent)
    Output: list of anomaly alerts, budget breach alerts, and an
            overall alert summary.
    """

    # Give the LLM the full transaction list so it can compare charges
    transaction_text = "\n".join(
        f"  {t['date']} | {t['description']} | ${t['amount']:.2f}"
        for t in expenses
    )

    # Pass the recommended budget so it can flag breaches
    recommended_budget = budget_analysis.get("recommended_budget", {})
    overspending       = budget_analysis.get("overspending", [])

    system_prompt = """You are a financial compliance and anomaly detection AI.
Your job is to scan transactions for two things:

1. ANOMALY ALERTS: Find any merchant where one charge is significantly
   higher than other charges from the same merchant in the data.
   Example: Uber Eats appears 3x at ~$20 and once at $120 — flag it.

2. BUDGET ALERTS: Flag any spending category that has exceeded its
   recommended budget limit.

Severity levels: "high", "medium", "low"

Respond ONLY with valid JSON — no markdown, no explanation.
Format:
{
  "anomaly_alerts": [
    {
      "merchant": "Uber Eats",
      "typical_amount": 20.00,
      "flagged_amount": 120.00,
      "severity": "high",
      "message": "Charge 6x higher than typical spend at this merchant."
    }
  ],
  "budget_alerts": [
    {
      "category": "Entertainment",
      "budget_limit": 200.00,
      "actual_spend": 250.00,
      "severity": "medium",
      "message": "Entertainment spending exceeded budget by $50."
    }
  ],
  "total_alerts": 2,
  "alert_summary": "One sentence summary of the alert status."
}"""

    user_prompt = f"""
Transactions This Month:
{transaction_text}

Recommended Budget by Category:
{json.dumps(recommended_budget, indent=2)}

Known Overspending (from Budget Agent):
{json.dumps(overspending, indent=2)}

Generate anomaly and budget alerts based on this data.
"""

    raw = ask_llm(system_prompt, user_prompt)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "raw_alerts":     raw,
            "anomaly_alerts": [],
            "budget_alerts":  [],
            "total_alerts":   0,
        }

    return result