import json
import re
from typing import Any, Dict


# ============================================================
# ENTITY EXTRACTION PROMPT
# ============================================================

ENTITY_PROMPT = """
You are a legal contract information extraction system.

Extract important structured entities from the contract.

Return ONLY valid JSON.

Use exactly this structure:

{
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
}

Rules:

1. "parties":
   Include the legal names of companies, organizations, or individuals
   that are parties to the agreement.

2. "agreement_date":
   The date on which the agreement was signed/executed.

3. "effective_date":
   The date on which the agreement becomes effective.

4. "expiration_date":
   The date on which the initial contract term expires.

5. "renewal_term":
   Include automatic renewal or extension terms.

6. "governing_law":
   Identify the state/country whose law governs the agreement.

7. "jurisdiction":
   Identify courts, locations, or jurisdictions specified for disputes.

8. "notice_periods":
   Extract termination, renewal, or other contractual notice periods.

9. "monetary_amounts":
   Extract important amounts such as fees, payments, damages,
   minimum commitments, or royalties.

10. "payment_terms":
    Extract when and how payments must be made.

11. "contract_duration":
    Extract the initial term/duration of the agreement.

12. "other_entities":
    Include important structured information that does not fit
    into the above fields.

Do not invent information.
If an entity is not present, use null or [].
"""


# ============================================================
# GEMINI CALL
# ============================================================

def extract_entities(contract_text: str) -> Dict[str, Any]:
    """
    Extract structured entities from a contract using Gemini.
    """

    if not contract_text or not contract_text.strip():
        return {
            "success": False,
            "message": "Contract text is empty."
        }

    try:

        # Import your existing Gemini client/module.
        #
        # IMPORTANT:
        # Replace this import with the same Gemini setup
        # already used in your clause_extractor.py if necessary.

        from google import genai
        import os

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
            ENTITY_PROMPT
            + "\n\nCONTRACT:\n"
            + contract_text
        )

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        response_text = response.text.strip()

        # Remove markdown JSON fences if Gemini returns them
        response_text = re.sub(
            r"^```json\s*",
            "",
            response_text,
            flags=re.IGNORECASE
        )

        response_text = re.sub(
            r"\s*```$",
            "",
            response_text
        )

        data = json.loads(
            response_text
        )

        return {
            "success": True,
            "entities": data
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