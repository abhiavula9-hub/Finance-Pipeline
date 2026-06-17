"""
core/config.py
Centralised configuration — loads environment variables and exposes
settings that every module imports from here (not scattered os.getenv calls).
"""

import os
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()

# ── OpenAI ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")   # cheap & capable

# ── App settings ────────────────────────────────────────────────────────────
APP_TITLE: str = "Personal Finance AI"
APP_VERSION: str = "1.0.0"

# Default monthly budget targets (USD) — used by Budget Agent as baseline
DEFAULT_BUDGET: dict = {
    "Housing":        800,
    "Food":           300,
    "Entertainment":  150,
    "Transportation": 200,
    "Shopping":       250,
    "Subscriptions":  50,
    "Savings":        500,
    "Other":          150,
}

# ── Sanity check ────────────────────────────────────────────────────────────
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY not found. "
        "Create a .env file in the project root with: OPENAI_API_KEY=sk-..."
    )
