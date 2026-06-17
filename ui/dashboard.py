"""
ui/dashboard.py
Streamlit Dashboard — the user-facing interface.
Users upload a CSV here; the dashboard calls the Supervisor and
renders the results as charts and a written report.

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

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance AI",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Personal Finance AI Advisor")
st.caption("Upload your transactions CSV and get an instant AI-powered financial report.")

# ── Sidebar: file upload ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Transactions")
    uploaded_file = st.file_uploader("Choose a .csv file", type=["csv"])
    st.markdown("**Expected columns:** Date, Description, Amount")
    st.markdown("Negative amounts = expenses | Positive = income")

    # Sample data download so users can test immediately
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
2026-06-13,Uber Eats,-30.00
"""
    st.download_button(
        label="⬇ Download sample CSV",
        data=sample_csv,
        file_name="sample_transactions.csv",
        mime="text/csv",
    )

# ── Main area ────────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.info("👈 Upload a CSV file in the sidebar to get started.")
    st.stop()

# Read the CSV and run the pipeline when a file is uploaded
csv_content = uploaded_file.read().decode("utf-8")

with st.spinner("🤖 Running AI pipeline... (Expense → Budget → Savings → Report)"):
    try:
        results = run_supervisor(csv_content)
    except Exception as e:
        st.error(f"Pipeline error: {e}")
        st.stop()

# Unpack agent results
expense_data  = results["expense_analysis"]
budget_data   = results["budget_analysis"]
savings_data  = results["savings_analysis"]
report_data   = results["report"]
metrics       = report_data["metrics"]

# ── Headline metric cards ────────────────────────────────────────────────────
st.subheader("📊 Financial Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Income",    f"${metrics['income']:,.2f}")
col2.metric("Monthly Expenses",  f"${metrics['expenses']:,.2f}")
col3.metric("Remaining Balance", f"${metrics['remaining']:,.2f}")
col4.metric("Savings Rate",      f"{metrics['savings_rate']:.1f}%")

st.divider()

# ── Charts row ───────────────────────────────────────────────────────────────
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
    actual      = expense_data.get("categories", {})
    all_cats    = sorted(set(list(recommended.keys()) + list(actual.keys())))

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Recommended",
        x=all_cats,
        y=[recommended.get(c, 0) for c in all_cats],
        marker_color="steelblue",
    ))
    fig_bar.add_trace(go.Bar(
        name="Actual",
        x=all_cats,
        y=[actual.get(c, 0) for c in all_cats],
        marker_color="tomato",
    ))
    fig_bar.update_layout(barmode="group", title="Budget vs Actual Spending")
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Overspending alerts ──────────────────────────────────────────────────────
st.subheader("⚠️ Overspending Alerts")
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
    st.success("✅ No overspending detected!")

st.divider()

# ── Savings opportunities ────────────────────────────────────────────────────
st.subheader("💡 Savings Opportunities")
opportunities = savings_data.get("savings_opportunities", [])
if opportunities:
    opp_df = pd.DataFrame(opportunities)
    st.dataframe(opp_df, use_container_width=True)
    total_annual = savings_data.get("total_annual_savings", 0)
    st.success(f"💰 Potential Annual Savings: **${total_annual:,.2f}**")

st.divider()

# ── Full AI Report ───────────────────────────────────────────────────────────
st.subheader("📄 Full Financial Health Report")
with st.expander("Click to expand the full AI-generated report", expanded=True):
    st.markdown(report_data.get("report_markdown", "Report not available."))

# ── Raw transactions table ───────────────────────────────────────────────────
st.subheader("🧾 Your Transactions")
transactions = expense_data.get("transactions", [])
if transactions:
    df = pd.DataFrame(transactions)
    st.dataframe(df, use_container_width=True)
