"""
agents/expense_agent.py
Expense Analysis Agent — takes raw expense transactions and uses the LLM
to categorise them, then computes summary stats.
"""

import json
from typing import List, Dict, Any
from tools.finance_tools import ask_llm


def run_expense_agent(expenses: List[Dict]) -> Dict[str, Any]:
    """
    Input : list of expense dicts  {"date", "description", "amount"}
    Output: dict with category totals, top merchant, highest expense, etc.
    """

    # Format transactions as a simple text block for the LLM
    transaction_text = "\n".join(
        f"{t['description']} - ${t['amount']:.2f}" for t in expenses
    )

    system_prompt = """You are a financial analyst AI.
Your job is to categorise transactions into these buckets:
Food, Shopping, Entertainment, Transportation, Subscriptions, Housing, Other.

Respond ONLY with a valid JSON object — no markdown, no explanation.
Format:
{
  "categories": {"Food": 45.00, "Shopping": 95.20, ...},
  "most_spending_category": "Food",
  "most_frequent_merchant": "Starbucks",
  "highest_expense": {"description": "Walmart", "amount": 95.20}
}"""

    user_prompt = f"Categorise these transactions:\n{transaction_text}"

    # Call the LLM and parse response
    raw = ask_llm(system_prompt, user_prompt)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return raw text so the pipeline doesn't crash
        result = {"raw_analysis": raw, "categories": {}}

    # Attach the original list so downstream agents can reuse it
    result["transactions"] = expenses
    return result
