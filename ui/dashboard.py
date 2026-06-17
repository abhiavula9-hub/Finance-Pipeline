"""
ui/dashboard.py
Streamlit Dashboard — user-facing interface for the full pipeline.
Users upload a CSV; dashboard runs all 7 agents and renders results
as charts, metric cards, alert panels, and a written report.

Updated sections:
  - Forecast panel showing next-month prediction     ← NEW
  - Alerts panel showing anomalies & budget breaches ← NEW

Run with:  streamlit run ui/dashboard.py  (from project root)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from agents.supervisor import run_supervisor

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance AI",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Personal Finance AI Advisor")
st.caption("Upload your transactions CSV and get an instant AI-powered financial report.")

# ── Sidebar: file upload + sample download ───────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Transactions")
    uploaded_file = st.file_uploader("Choose a .csv file", type=["csv"])
    st.markdown("**Expected columns:** Date, Description, Amount")
    st.markdown("Negative amounts = expenses | Positive = income")

    sample_csv = """Date,Description,Amount
2026-06-01,Starbucks,-8.50
2026-06-02,Walmart,-95.20
2026-06-03,Netflix,-15.99
2026-06-04,Spotify,-12.00
2026-06-05,Salary,2500.00
2026-06-06,Uber Eats,-22.15
2026-06-07,Starbucks,-9.00
2026-06-08,Amazon,-65.00
2026-06-09,Uber Eats,-18.50
2026-06-10,Gym Membership,-40.00
2026-06-11,Starbucks,-8.50
2026-06-12,Walmart,-112.00
2026-06-13,Uber Eats,-120.00
"""
    # Sample CSV includes a suspicious $120 Uber Eats charge to trigger the Alert Agent
    st.download_button(
        label="⬇ Download sample CSV",
        data=sample_csv,
        file_name="sample_transactions.csv",
        mime="text/csv",
    )

# ── Gate: stop here if no file uploaded ─────────────────────────────────────
if uploaded_file is None:
    st.info("👈 Upload a CSV file in the sidebar to get started.")
    st.stop()

# ── Run the full 7-agent pipeline ────────────────────────────────────────────
csv_content = uploaded_file.read().decode("utf-8")

with st.spinner("🤖 Running AI pipeline... (Expense → Budget → Savings → Forecast → Alerts → Report)"):
    try:
        results = run_supervisor(csv_content)
    except Exception as e:
        st.error(f"Pipeline error: {e}")
        st.stop()

# Unpack all agent results
expense_data  = results["expense_analysis"]
budget_data   = results["budget_analysis"]
savings_data  = results["savings_analysis"]
forecast_data = results["forecast_analysis"]   # NEW
alert_data    = results["alert_analysis"]       # NEW
report_data   = results["report"]
metrics       = report_data["metrics"]

# ── Section 1: Headline metric cards ─────────────────────────────────────────
st.subheader("📊 Financial Overview")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Monthly Income",       f"${metrics['income']:,.2f}")
col2.metric("Monthly Expenses",     f"${metrics['expenses']:,.2f}")
col3.metric("Remaining Balance",    f"${metrics['remaining']:,.2f}")
col4.metric("Savings Rate",         f"{metrics['savings_rate']:.1f}%")
# Alert count shown as a metric so it's visible at a glance
col5.metric("Active Alerts",        str(metrics.get("total_alerts", 0)),
            delta_color="inverse")

st.divider()

# ── Section 2: Spending charts ───────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🥧 Spending by Category")
    categories = expense_data.get("categories", {})
    if categories:
        fig_pie = px.pie(
            names=list(categories.keys()),
            values=list(categories.values()),
            title="Expense Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📉 Actual vs Recommended Budget")
    recommended = budget_data.get("recommended_budget", {})
    actual      = expense_data.get("categories",        {})
    all_cats    = sorted(set(list(recommended.keys()) + list(actual.keys())))

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Recommended", x=all_cats,
        y=[recommended.get(c, 0) for c in all_cats],
        marker_color="steelblue",
    ))
    fig_bar.add_trace(go.Bar(
        name="Actual", x=all_cats,
        y=[actual.get(c, 0) for c in all_cats],
        marker_color="tomato",
    ))
    fig_bar.update_layout(barmode="group", title="Budget vs Actual Spending")
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Section 3: Forecast (NEW) ────────────────────────────────────────────────
st.subheader("🔮 Spending Forecast — Next Month")

fc_col1, fc_col2, fc_col3 = st.columns(3)
fc_col1.metric("Predicted Total Spend",  f"${forecast_data.get('predicted_total', 0):,.2f}")
fc_col2.metric("Highest Risk Category",  forecast_data.get("highest_risk_category", "N/A"))
fc_col3.metric("Expected Change",        f"{forecast_data.get('expected_change_pct', 0):.1f}%")

# Bar chart: current vs predicted by category
predicted = forecast_data.get("predicted_spending", {})
if predicted and categories:
    forecast_cats = sorted(set(list(categories.keys()) + list(predicted.keys())))
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Bar(
        name="This Month",  x=forecast_cats,
        y=[categories.get(c, 0) for c in forecast_cats],
        marker_color="mediumseagreen",
    ))
    fig_forecast.add_trace(go.Bar(
        name="Predicted Next Month", x=forecast_cats,
        y=[predicted.get(c, 0) for c in forecast_cats],
        marker_color="darkorange",
    ))
    fig_forecast.update_layout(barmode="group", title="Current vs Predicted Spending by Category")
    st.plotly_chart(fig_forecast, use_container_width=True)

if forecast_data.get("forecast_summary"):
    st.info(f"📈 {forecast_data['forecast_summary']}")

st.divider()

# ── Section 4: Alerts (NEW) ──────────────────────────────────────────────────
st.subheader("🚨 Alerts & Anomalies")

anomaly_alerts = alert_data.get("anomaly_alerts", [])
budget_alerts  = alert_data.get("budget_alerts",  [])

if not anomaly_alerts and not budget_alerts:
    st.success("✅ No alerts detected. Everything looks normal.")
else:
    # Anomaly alerts — unusual charges vs typical merchant spend
    if anomaly_alerts:
        st.markdown("**🔍 Anomaly Alerts**")
        for a in anomaly_alerts:
            severity_icon = "🔴" if a.get("severity") == "high" else "🟡"
            st.error(
                f"{severity_icon} **{a.get('merchant')}** — "
                f"Typical: ${a.get('typical_amount', 0):.2f} | "
                f"Flagged charge: **${a.get('flagged_amount', 0):.2f}** | "
                f"{a.get('message', '')}"
            )

    # Budget alerts — categories that exceeded recommended limits
    if budget_alerts:
        st.markdown("**💳 Budget Breach Alerts**")
        for b in budget_alerts:
            severity_icon = "🔴" if b.get("severity") == "high" else "🟡"
            st.warning(
                f"{severity_icon} **{b.get('category')}** — "
                f"Limit: ${b.get('budget_limit', 0):.2f} | "
                f"Actual: ${b.get('actual_spend', 0):.2f} | "
                f"{b.get('message', '')}"
            )

    if alert_data.get("alert_summary"):
        st.caption(f"ℹ️ {alert_data['alert_summary']}")

st.divider()

# ── Section 5: Overspending ──────────────────────────────────────────────────
st.subheader("⚠️ Budget Overspending")
overspending = report_data.get("overspending", [])
if overspending:
    for alert in overspending:
        st.warning(
            f"**{alert.get('category')}** — "
            f"Recommended: ${alert.get('recommended', 0):.0f} | "
            f"Actual: ${alert.get('actual', 0):.0f} | "
            f"Over by: **${alert.get('overspent_by', 0):.0f}**"
        )
else:
    st.success("✅ Spending within budget across all categories.")

st.divider()

# ── Section 6: Savings opportunities ────────────────────────────────────────
st.subheader("💡 Savings Opportunities")
opportunities = savings_data.get("savings_opportunities", [])
if opportunities:
    opp_df = pd.DataFrame(opportunities)
    st.dataframe(opp_df, use_container_width=True)
    st.success(f"💰 Potential Annual Savings: **${savings_data.get('total_annual_savings', 0):,.2f}**")

st.divider()

# ── Section 7: Full AI Report ─────────────────────────────────────────────────
st.subheader("📄 Full Financial Health Report")
with st.expander("Click to expand the full AI-generated report", expanded=True):
    st.markdown(report_data.get("report_markdown", "Report not available."))

# ── Section 8: Raw transactions table ────────────────────────────────────────
st.subheader("🧾 Your Transactions")
transactions = expense_data.get("transactions", [])
if transactions:
    df = pd.DataFrame(transactions)
    st.dataframe(df, use_container_width=True)
