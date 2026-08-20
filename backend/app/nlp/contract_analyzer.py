import json
import os
import re
from typing import Any, Dict

from google import genai


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


# ============================================================
# UNIFIED CONTRACT ANALYSIS PROMPT
# ============================================================

CONTRACT_ANALYSIS_PROMPT = """
You are an AI-powered legal contract analysis system.

Analyze the provided contract and extract the following information:

1. Contract summary
2. Contract clauses
3. Important entities
4. Contractual obligations
5. Important dates, amounts, notice periods and payment terms

Return ONLY valid JSON.

Do not return markdown.
Do not use ```json.
Do not add explanations outside the JSON.

Use EXACTLY this structure:

{
    "summary": "",

    "clauses": {
        "Parties": "",
        "Agreement Date": "",
        "Effective Date": "",
        "Term": "",
        "Termination": "",
        "Renewal": "",
        "Payment Terms": "",
        "Confidentiality": "",
        "Intellectual Property": "",
        "Limitation of Liability": "",
        "Indemnification": "",
        "Governing Law": "",
        "Dispute Resolution": "",
        "Insurance": "",
        "Non-Compete": "",
        "Non-Solicitation": "",
        "Assignment": "",
        "Force Majeure": "",
        "Notices": "",
        "Other": ""
    },

    "entities": {
        "parties": [],
        "agreement_date": null,
        "effective_date": null,
        "expiration_date": null,
        "renewal_term": null,
        "governing_law": null,
        "jurisdiction": null,
        "notice_periods": [],
        "monetary_amounts": [],
        "payment_terms": [],
        "contract_duration": null,
        "other_entities": []
    },

    "obligations": [
        {
            "obligation": "",
            "responsible_party": "",
            "deadline": "",
            "frequency": "",
            "trigger": "",
            "category": "",
            "consequence": "",
            "evidence": ""
        }
    ]
}

IMPORTANT RULES:

- Do NOT invent information.
- If information is not present, use null, "", or [].
- Preserve the meaning of the contract.
- Use the exact contractual language where appropriate.
- "clauses" should contain the relevant clause text, not a generic description.
- "entities" should contain structured information.
- "obligations" should contain actual duties or responsibilities imposed by the contract.
- Include deadlines, notice periods and payment dates whenever explicitly stated.
- If a clause category is not present, return an empty string.
- Return valid JSON only.
"""


# ============================================================
# JSON CLEANER
# ============================================================

def clean_json_response(response_text: str) -> str:

    response_text = response_text.strip()

    # Remove ```json
    response_text = re.sub(
        r"^```json\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    # Remove ```
    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )

    return response_text.strip()


# ============================================================
# MAIN ANALYZER
# ============================================================

def analyze_contract(
    contract_text: str
) -> Dict[str, Any]:

    if not contract_text or not contract_text.strip():

        return {
            "success": False,
            "message": "Contract text is empty."
        }

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        return {
            "success": False,
            "message": "GEMINI_API_KEY is not configured."
        }

    try:

        client = genai.Client(
            api_key=api_key
        )

        prompt = (
            CONTRACT_ANALYSIS_PROMPT
            + "\n\nCONTRACT:\n"
            + contract_text
        )

        # ----------------------------------------------------
        # ONE GEMINI REQUEST
        # ----------------------------------------------------

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        response_text = response.text.strip()

        response_text = clean_json_response(
            response_text
        )

        data = json.loads(
            response_text
        )

        return {
            "success": True,
            "analysis": data
        }

    except json.JSONDecodeError as e:

        return {
            "success": False,
            "message": "Gemini returned invalid JSON.",
            "raw_response": (
                response.text
                if "response" in locals()
                else ""
            ),
            "error": str(e)
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }