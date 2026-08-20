"""
Summarize a full contract in plain English. No retrieval needed here —
unlike chat Q&A, we want the whole document considered at once, so we
send the full text directly to Gemini rather than searching for relevant
chunks first.
"""
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_SUMMARY_PROMPT = """You are a legal contract assistant. Summarize the \
following contract in plain, non-legal English for someone with no legal \
background. Cover:

1. Who the parties are and what the contract is for
2. The key obligations of each party
3. Payment terms, if any
4. Termination/cancellation terms, if any
5. Any notably one-sided, unusual, or risky terms worth flagging

Keep it concise — use short paragraphs or bullet points, not a wall of text.

Contract text:
{contract_text}"""


def summarize_contract(contract_text: str) -> str:
    model = genai.GenerativeModel("gemini-flash-latest")
    prompt = _SUMMARY_PROMPT.format(contract_text=contract_text)
    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    # quick manual test: python -m app.rag.summarizer
    sample = """LEGAL SERVICES AGREEMENT. This agreement is between Law Firm
    and Client. Client must pay by the hour per the Rate Schedule. Either
    party may terminate with 30 days written notice."""
    print(summarize_contract(sample))