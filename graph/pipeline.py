"""
graph/pipeline.py
LangGraph Pipeline — defines the state graph that wires all agents together.
Each node in the graph is one agent call. State flows through all nodes
in sequence, accumulating results at each step.

Updated graph structure:
  START
    └── parse_node
          └── expense_node
                └── budget_node
                      └── savings_node
                            └── forecast_node  ← NEW
                                  └── alert_node  ← NEW
                                        └── report_node
                                              └── END
"""

from typing import TypedDict, Any, Dict, List
from langgraph.graph import StateGraph, END

from tools.csv_parser import (
    parse_transactions,
    split_income_expenses,
    total_income as calc_total_income,
    total_expenses as calc_total_expenses,
)
from agents.expense_agent  import run_expense_agent
from agents.budget_agent   import run_budget_agent
from agents.savings_agent  import run_savings_agent
from agents.forecast_agent import run_forecast_agent   # NEW
from agents.alert_agent    import run_alert_agent       # NEW
from agents.report_agent   import run_report_agent


# ── Shared state — this dict is passed between every node ────────────────────
# Each node reads what it needs and adds its own output key.

class FinanceState(TypedDict):
    csv_content:       str
    transactions:      List
    income_txns:       List
    expense_txns:      List
    total_income:      float
    total_expenses:    float
    expense_analysis:  Dict[str, Any]
    budget_analysis:   Dict[str, Any]
    savings_analysis:  Dict[str, Any]
    forecast_analysis: Dict[str, Any]   # NEW
    alert_analysis:    Dict[str, Any]   # NEW
    report:            Dict[str, Any]


# ── Node functions ────────────────────────────────────────────────────────────

def parse_node(state: FinanceState) -> FinanceState:
    """Node 1: Parse the raw CSV into income and expense lists."""
    txns = parse_transactions(state["csv_content"])
    inc, exp = split_income_expenses(txns)
    return {
        **state,
        "transactions":   txns,
        "income_txns":    inc,
        "expense_txns":   exp,
        "total_income":   calc_total_income(inc),
        "total_expenses": calc_total_expenses(exp),
    }


def expense_node(state: FinanceState) -> FinanceState:
    """Node 2: Categorise expenses and identify top merchant/category."""
    result = run_expense_agent(state["expense_txns"])
    return {**state, "expense_analysis": result}


def budget_node(state: FinanceState) -> FinanceState:
    """Node 3: Compare actual category spend against recommended budget."""
    result = run_budget_agent(state["expense_analysis"], state["total_income"])
    return {**state, "budget_analysis": result}


def savings_node(state: FinanceState) -> FinanceState:
    """Node 4: Find recurring costs and savings opportunities."""
    result = run_savings_agent(state["expense_txns"], state["total_income"])
    return {**state, "savings_analysis": result}


def forecast_node(state: FinanceState) -> FinanceState:
    """Node 5 (NEW): Predict next month's spending based on current patterns."""
    result = run_forecast_agent(state["expense_txns"], state["expense_analysis"])
    return {**state, "forecast_analysis": result}


def alert_node(state: FinanceState) -> FinanceState:
    """Node 6 (NEW): Flag anomalous charges and budget breaches."""
    result = run_alert_agent(state["expense_txns"], state["budget_analysis"])
    return {**state, "alert_analysis": result}


def report_node(state: FinanceState) -> FinanceState:
    """Node 7: Aggregate all agent outputs into the final report."""
    result = run_report_agent(
        state["expense_analysis"],
        state["budget_analysis"],
        state["savings_analysis"],
        state["forecast_analysis"],   # NEW
        state["alert_analysis"],      # NEW
    )
    return {**state, "report": result}


# ── Build and compile the graph ───────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    """
    Register all nodes and wire them in sequence.
    Returns a compiled LangGraph pipeline ready to invoke.
    """
    graph = StateGraph(FinanceState)

    # Register every node by name
    graph.add_node("parse",    parse_node)
    graph.add_node("expense",  expense_node)
    graph.add_node("budget",   budget_node)
    graph.add_node("savings",  savings_node)
    graph.add_node("forecast", forecast_node)   # NEW
    graph.add_node("alert",    alert_node)       # NEW
    graph.add_node("report",   report_node)

    # Wire nodes in sequence: each one feeds into the next
    graph.set_entry_point("parse")
    graph.add_edge("parse",    "expense")
    graph.add_edge("expense",  "budget")
    graph.add_edge("budget",   "savings")
    graph.add_edge("savings",  "forecast")   # NEW
    graph.add_edge("forecast", "alert")      # NEW
    graph.add_edge("alert",    "report")
    graph.add_edge("report",   END)

    return graph.compile()


# Single compiled pipeline instance — imported by supervisor and API
pipeline = build_pipeline()