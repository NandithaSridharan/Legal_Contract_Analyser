import difflib


def compare_contracts(
    text1: str,
    text2: str
):

    if not text1 or not text2:

        return {
            "success": False,
            "message": (
                "Both contract texts are required."
            )
        }

    diff = difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        fromfile="Contract A",
        tofile="Contract B",
        lineterm=""
    )

    changes = []

    for line in diff:

        if (
            line.startswith("+++")
            or line.startswith("---")
            or line.startswith("@@")
        ):
            continue

        if line.startswith("+"):

            changes.append({
                "type": "ADDED",
                "text": line[1:]
            })

        elif line.startswith("-"):

            changes.append({
                "type": "REMOVED",
                "text": line[1:]
            })

    return {
        "success": True,
        "total_changes": len(changes),
        "changes": changes
    }