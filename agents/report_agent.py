"""
agents/report_agent.py
Report Agent — the final agent in the pipeline.
Receives all previous agents' outputs and synthesises a human-readable
Financial Health Report.
"""

from typing import Dict, Any
from tools.finance_tools import ask_llm


def run_report_agent(
    expense_analysis: Dict,
    budget_analysis: Dict,
    savings_analysis: Dict,
) -> Dict[str, Any]:
    """
    Input : outputs from expense_agent, budget_agent, savings_agent
    Output: dict with a formatted markdown report and key headline metrics.
    """

    # Pull headline numbers from prior agents
    income         = budget_analysis.get("total_income",    0)
    expenses       = budget_analysis.get("total_expenses",  0)
    remaining      = budget_analysis.get("remaining_balance", income - expenses)
    savings_rate   = savings_analysis.get("current_savings_rate_pct", 0)
    top_category   = expense_analysis.get("most_spending_category", "N/A")
    overspending   = budget_analysis.get("overspending", [])
    opportunities  = savings_analysis.get("savings_opportunities", [])
    annual_savings = savings_analysis.get("total_annual_savings", 0)

    system_prompt = """You are a financial report writer.
Write a clear, friendly Financial Health Report in Markdown format.
Include sections: Overview, Spending Breakdown, Budget Analysis,
Savings Opportunities, and Recommendations.
Be specific with the numbers provided."""

    user_prompt = f"""
Monthly Income   : ${income:.2f}
Monthly Expenses : ${expenses:.2f}
Remaining Balance: ${remaining:.2f}
Savings Rate     : {savings_rate:.1f}%
Top Spend Category: {top_category}
Overspending Alerts: {overspending}
Savings Opportunities: {opportunities}
Potential Annual Savings: ${annual_savings:.2f}

Write the full Financial Health Report now.
"""

    report_text = ask_llm(system_prompt, user_prompt)

    return {
        "report_markdown": report_text,
        # Headline metrics also returned so the dashboard can display them directly
        "metrics": {
            "income":         income,
            "expenses":       expenses,
            "remaining":      remaining,
            "savings_rate":   savings_rate,
            "top_category":   top_category,
            "annual_savings": annual_savings,
        },
        "overspending":  overspending,
        "opportunities": opportunities,
    }
