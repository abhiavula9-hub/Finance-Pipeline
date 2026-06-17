"""
tools/finance_tools.py
Shared LLM helper used by all agents.
Wraps the OpenAI chat completion call so agents don't
repeat boilerplate — just call ask_llm(system, user).
"""

from openai import OpenAI
from core.config import OPENAI_API_KEY, MODEL_NAME

# One shared client instance for the whole app
_client = OpenAI(api_key=OPENAI_API_KEY)


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Send a system + user message to the LLM and return the text response.
    All agents funnel through here so model/token settings live in one place.
    """
    response = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_prompt},
        ],
        temperature=0.3,      # Low temp = consistent, factual financial output
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()
