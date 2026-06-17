"""
graph/pipeline.py
LangGraph Pipeline — defines the state graph that wires all agents together.
Each node in the graph corresponds to one agent call.

Graph structure:
  START
    └── parse_node
          └── expense_node
                └── budget_node
                      └── savings_node
                            └── report_node
                                  └── END
"""

from typing import TypedDict, Any, Dict
from langgraph.graph import StateGraph, END

from tools.csv_parser import (
    parse_transactions,
    split_income_expenses,
    total_income as calc_total_income,
    total_expenses as calc_total_expenses,
)
from agents.expense_agent import run_expense_agent
from agents.budget_agent   import run_budget_agent
from agents.savings_agent  import run_savings_agent
from agents.report_agent   import run_report_agent


# ── Shared state object passed between graph nodes ───────────────────────────

class FinanceState(TypedDict):
    csv_content:      str           # Raw CSV string — set at graph entry
    transactions:     list          # Parsed list of all transaction dicts
    income_txns:      list          # Income-only transactions
    expense_txns:     list          # Expense-only transactions
    total_income:     float
    total_expenses:   float
    expense_analysis: Dict[str, Any]
    budget_analysis:  Dict[str, Any]
    savings_analysis: Dict[str, Any]
    report:           Dict[str, Any]


# ── Node functions (one per agent) ──────────────────────────────────────────

def parse_node(state: FinanceState) -> FinanceState:
    """Node 1: Parse the CSV and split into income / expenses."""
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
    """Node 2: Run the Expense Analysis Agent."""
    result = run_expense_agent(state["expense_txns"])
    return {**state, "expense_analysis": result}


def budget_node(state: FinanceState) -> FinanceState:
    """Node 3: Run the Budget Agent."""
    result = run_budget_agent(state["expense_analysis"], state["total_income"])
    return {**state, "budget_analysis": result}


def savings_node(state: FinanceState) -> FinanceState:
    """Node 4: Run the Savings Agent."""
    result = run_savings_agent(state["expense_txns"], state["total_income"])
    return {**state, "savings_analysis": result}


def report_node(state: FinanceState) -> FinanceState:
    """Node 5: Run the Report Agent — final synthesis step."""
    result = run_report_agent(
        state["expense_analysis"],
        state["budget_analysis"],
        state["savings_analysis"],
    )
    return {**state, "report": result}


# ── Build the graph ──────────────────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    """
    Assemble and compile the LangGraph pipeline.
    Returns a compiled graph ready to invoke.
    """
    graph = StateGraph(FinanceState)

    # Register all nodes
    graph.add_node("parse",    parse_node)
    graph.add_node("expense",  expense_node)
    graph.add_node("budget",   budget_node)
    graph.add_node("savings",  savings_node)
    graph.add_node("report",   report_node)

    # Wire them in sequence: parse → expense → budget → savings → report → END
    graph.set_entry_point("parse")
    graph.add_edge("parse",   "expense")
    graph.add_edge("expense", "budget")
    graph.add_edge("budget",  "savings")
    graph.add_edge("savings", "report")
    graph.add_edge("report",  END)

    return graph.compile()


# Expose a single compiled pipeline instance
pipeline = build_pipeline()
