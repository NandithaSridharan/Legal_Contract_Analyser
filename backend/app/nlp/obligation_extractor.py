import json
import os
import re
from typing import Any, Dict


# ============================================================
# PROMPT
# ============================================================

OBLIGATION_PROMPT = """
You are a legal contract obligation and deadline extraction system.

Analyze the contract and identify important obligations,
deadlines, notice periods, recurring requirements, and
actions that a party must perform.

Return ONLY valid JSON.

Use exactly this structure:

{
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

Extraction rules:

1. obligation:
   Describe the action or responsibility that must be performed.

2. responsible_party:
   Identify which party is responsible.
   Do not invent a party if it cannot be determined.

3. deadline:
   Extract an explicit deadline, date, time period,
   or notice period.

4. frequency:
   Extract recurring frequency such as monthly, quarterly,
   annually, or one-time.

5. trigger:
   Identify what starts the deadline.
   Examples:
   - receipt of invoice
   - termination
   - effective date
   - end of contract year
   - occurrence of an event

6. category:
   Classify the obligation using categories such as:
   - Payment
   - Termination
   - Renewal
   - Notice
   - Reporting
   - Delivery
   - Insurance
   - Confidentiality
   - Intellectual Property
   - Audit
   - Compliance
   - Other

7. consequence:
   Extract the consequence of failing to perform the obligation
   ONLY if explicitly stated in the contract.

8. evidence:
   Include the relevant contract wording supporting the extraction.

Important:
- Do not invent information.
- Do not infer a deadline when one is not explicitly stated.
- Preserve the meaning of the contract.
- If no obligations are found, return an empty list.
"""


# ============================================================
# CLEAN GEMINI RESPONSE
# ============================================================

def clean_json_response(text: str) -> str:

    text = text.strip()

    # Remove ```json
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove ```
    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE OBLIGATION
# ============================================================

def normalize_obligation(
    item: Dict[str, Any]
) -> Dict[str, Any]:

    return {
        "obligation": item.get(
            "obligation"
        ),

        "responsible_party": item.get(
            "responsible_party"
        ),

        "deadline": item.get(
            "deadline"
        ),

        "frequency": item.get(
            "frequency"
        ),

        "trigger": item.get(
            "trigger"
        ),

        "category": item.get(
            "category"
        ),

        "consequence": item.get(
            "consequence"
        ),

        "evidence": item.get(
            "evidence"
        )
    }


# ============================================================
# EXTRACT OBLIGATIONS
# ============================================================

def extract_obligations(
    contract_text: str
) -> Dict[str, Any]:

    if not contract_text or not contract_text.strip():

        return {
            "success": False,
            "message": "Contract text is empty."
        }

    try:

        from google import genai

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        client = genai.Client(
            api_key=api_key
        )

        prompt = (
            OBLIGATION_PROMPT
            + "\n\nCONTRACT:\n"
            + contract_text
        )

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        response_text = clean_json_response(
            response.text
        )

        data = json.loads(
            response_text
        )

        # Make sure obligations exists
        if "obligations" not in data:

            data["obligations"] = []

        # Normalize each obligation
        normalized = []

        for item in data["obligations"]:

            if isinstance(
                item,
                dict
            ):

                normalized.append(
                    normalize_obligation(
                        item
                    )
                )

        data["obligations"] = normalized

        return {
            "success": True,
            **data
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