from typing import Dict, Any


def build_analysis_result(
    summary: Any,
    clauses: Any,
    risks: Any,
    entities: Any,
    obligations: Any,
    checklist: Any
) -> Dict:

    return {
        "success": True,

        "summary": summary,

        "clauses": clauses,

        "risk_analysis": risks,

        "entities": entities,

        "obligations": obligations,

        "checklist": checklist
    }