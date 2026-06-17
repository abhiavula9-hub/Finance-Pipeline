"""
agents/report_agent.py
Report Agent — the final agent in the pipeline.
Receives ALL previous agents' outputs and synthesises a single,
human-readable Financial Health Report in Markdown.

Updated to include Forecast and Alert data in the report.

Flow (this agent is always last):
  expense_agent output
  budget_agent output
  savings_agent output
  forecast_agent output  ← NEW
  alert_agent output     ← NEW
       └─> LLM writes the full report
             └─> Returns markdown + headline metrics dict
"""

from typing import Dict, Any
from tools.finance_tools import ask_llm


def run_report_agent(
    expense_analysis:  Dict,
    budget_analysis:   Dict,
    savings_analysis:  Dict,
    forecast_analysis: Dict = None,   # NEW
    alert_analysis:    Dict = None,   # NEW
) -> Dict[str, Any]:
    """
    Input : outputs from all upstream agents
    Output: dict with a formatted markdown report and key headline metrics.
    """

    # ── Pull headline numbers from prior agents ──────────────────────────────
    income         = budget_analysis.get("total_income",      0)
    expenses       = budget_analysis.get("total_expenses",    0)
    remaining      = budget_analysis.get("remaining_balance", income - expenses)
    savings_rate   = savings_analysis.get("current_savings_rate_pct", 0)
    top_category   = expense_analysis.get("most_spending_category", "N/A")
    overspending   = budget_analysis.get("overspending",       [])
    opportunities  = savings_analysis.get("savings_opportunities", [])
    annual_savings = savings_analysis.get("total_annual_savings",  0)

    # ── Pull forecast data (new) ─────────────────────────────────────────────
    forecast_total   = (forecast_analysis or {}).get("predicted_total",       0)
    risk_category    = (forecast_analysis or {}).get("highest_risk_category", "N/A")
    expected_change  = (forecast_analysis or {}).get("expected_change_pct",   0)
    forecast_summary = (forecast_analysis or {}).get("forecast_summary",      "")

    # ── Pull alert data (new) ────────────────────────────────────────────────
    anomaly_alerts = (alert_analysis or {}).get("anomaly_alerts", [])
    budget_alerts  = (alert_analysis or {}).get("budget_alerts",  [])
    total_alerts   = (alert_analysis or {}).get("total_alerts",   0)
    alert_summary  = (alert_analysis or {}).get("alert_summary",  "")

    system_prompt = """You are a financial report writer for a corporate fintech tool.
Write a clear, professional Financial Health Report in Markdown.

Include these sections in order:
1. Executive Summary
2. Income & Expense Overview
3. Spending Breakdown by Category
4. Budget Analysis (actual vs recommended)
5. Forecast (next month prediction)
6. Alerts & Anomalies
7. Savings Opportunities
8. Recommendations

Be specific with numbers. Keep a professional but readable tone."""

    user_prompt = f"""
Monthly Income        : ${income:.2f}
Monthly Expenses      : ${expenses:.2f}
Remaining Balance     : ${remaining:.2f}
Savings Rate          : {savings_rate:.1f}%
Top Spend Category    : {top_category}

Overspending Alerts   : {overspending}
Savings Opportunities : {opportunities}
Potential Annual Savings: ${annual_savings:.2f}

Forecast Next Month   : ${forecast_total:.2f}
Highest Risk Category : {risk_category}
Expected Change       : {expected_change:.1f}%
Forecast Note         : {forecast_summary}

Anomaly Alerts        : {anomaly_alerts}
Budget Alerts         : {budget_alerts}
Total Alerts          : {total_alerts}
Alert Summary         : {alert_summary}

Write the full Financial Health Report now.
"""

    report_text = ask_llm(system_prompt, user_prompt)

    return {
        "report_markdown": report_text,
        # Headline metrics returned separately so dashboard can display cards
        "metrics": {
            "income":         income,
            "expenses":       expenses,
            "remaining":      remaining,
            "savings_rate":   savings_rate,
            "top_category":   top_category,
            "annual_savings": annual_savings,
            "forecast_total": forecast_total,   # NEW
            "risk_category":  risk_category,    # NEW
            "total_alerts":   total_alerts,     # NEW
        },
        "overspending":   overspending,
        "opportunities":  opportunities,
        "anomaly_alerts": anomaly_alerts,   # NEW
        "budget_alerts":  budget_alerts,    # NEW
    }