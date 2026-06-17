# Personal Finance AI Pipeline

A multi-agent AI system built with LangGraph that analyzes personal financial transactions and generates a complete financial health report.

## What it does
A user uploads a CSV of bank transactions (date, description, amount). The pipeline runs the data through seven specialized AI agents in sequence, each handling a specific part of the analysis, and produces a final report with budget insights, spending forecasts, and anomaly alerts.

## Agent Pipeline
1. **Expense Agent** — categorizes transactions (Food, Shopping, Entertainment, etc.)
2. **Budget Agent** — compares actual spending against recommended budget limits
3. **Savings Agent** — identifies savings opportunities (subscriptions, recurring costs)
4. **Forecast Agent** — predicts next month's spending based on current patterns
5. **Alert Agent** — flags anomalous charges and budget breaches
6. **Report Agent** — synthesizes all outputs into one financial health report

The **Supervisor Agent** orchestrates the full sequence above.

## Tech Stack
- **LangGraph** — orchestrates the multi-agent pipeline as a state graph
- **OpenAI API** — powers each agent's analysis
- **Streamlit** — interactive dashboard frontend
- **FastAPI** — optional REST API backend
- **Plotly / Pandas** — data visualization and processing

## Project Structure
agents/     → All agent logic + supervisor
api/        → FastAPI backend (optional REST API)
core/       → Config and settings
graph/      → LangGraph pipeline definition
tools/      → CSV parsing and shared LLM helper
ui/         → Streamlit dashboard
main.py     → CLI entry point

## How to run

**Backend (terminal only):**
```bash
python main.py
```

**Frontend (Streamlit dashboard):**
```bash
streamlit run ui/dashboard.py
```

## Setup
1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file in the root with: `OPENAI_API_KEY=your-key-here`
6. Run `python main.py` or `streamlit run ui/dashboard.py`
