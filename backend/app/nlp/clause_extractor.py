"""
Extract clauses from a contract using CUAD's 41 clause categories as the
taxonomy. No training involved — this prompts Gemini to find and quote the
relevant text for each category, using CUAD's categories as a reference
schema rather than as training data.
"""
import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# CUAD's 41 clause categories (from the CUAD dataset schema).
CUAD_CATEGORIES = [
    "Document Name", "Parties", "Agreement Date", "Effective Date",
    "Expiration Date", "Renewal Term", "Notice Period To Terminate Renewal",
    "Governing Law", "Most Favored Nation", "Non-Compete",
    "Exclusivity", "No-Solicit Of Customers", "Competitive Restriction Exception",
    "No-Solicit Of Employees", "Non-Disparagement", "Termination For Convenience",
    "Rofr/Rofo/Rofn", "Change Of Control", "Anti-Assignment",
    "Revenue/Profit Sharing", "Price Restrictions", "Minimum Commitment",
    "Volume Restriction", "IP Ownership Assignment", "Joint IP Ownership",
    "License Grant", "Non-Transferable License", "Affiliate License-Licensor",
    "Affiliate License-Licensee", "Unlimited/All-You-Can-Eat License",
    "Irrevocable Or Perpetual License", "Source Code Escrow",
    "Post-Termination Services", "Audit Rights", "Uncapped Liability",
    "Cap On Liability", "Liquidated Damages", "Warranty Duration",
    "Insurance", "Covenant Not To Sue", "Indemnification",
]

_EXTRACTION_PROMPT = """You are a legal contract analysis assistant. Given \
the contract text below, identify which of the following clause categories \
are present, and quote the relevant excerpt for each one you find.

Categories:
{categories}

Contract text:
{contract_text}

Respond ONLY with valid JSON, no markdown formatting, no backticks, no \
preamble. Use this exact structure:
{{
  "CategoryName": "quoted excerpt from the contract, or null if not present",
  ...
}}
Only include categories that are actually present in the contract — omit \
categories with no match rather than including null values."""


def extract_clauses(contract_text: str) -> dict:
    model = genai.GenerativeModel("gemini-flash-latest")
    prompt = _EXTRACTION_PROMPT.format(
        categories=", ".join(CUAD_CATEGORIES),
        contract_text=contract_text,
    )
    response = model.generate_content(prompt)

    raw = response.text.strip()
    # Gemini sometimes wraps JSON in ```json fences despite instructions — strip if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Could not parse model output as JSON", "raw_output": raw}


if __name__ == "__main__":
    # quick manual test: python -m app.nlp.clause_extractor
    sample = """This agreement is between Law Firm and Client. Either party
    may terminate with 30 days written notice. Client agrees to pay by the
    hour per the attached Rate Schedule. This agreement is governed by the
    laws of California."""
    result = extract_clauses(sample)
    print(json.dumps(result, indent=2))