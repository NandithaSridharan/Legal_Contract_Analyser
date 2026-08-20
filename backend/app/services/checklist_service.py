from typing import Any, Dict, List


def create_checklist(obligations: Any) -> Dict[str, Any]:
    """
    Convert extracted obligations into actionable checklist items.
    """

    if isinstance(obligations, dict):
        obligations = obligations.get(
            "obligations",
            []
        )

    if not isinstance(obligations, list):
        obligations = []

    checklist: List[Dict[str, Any]] = []

    for index, item in enumerate(obligations, start=1):

        if not isinstance(item, dict):
            continue

        checklist.append({
            "id": index,

            "task": item.get(
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
            ),

            "completed": False
        })

    return {
        "success": True,
        "total_tasks": len(checklist),
        "completed_tasks": 0,
        "pending_tasks": len(checklist),
        "checklist": checklist
    }