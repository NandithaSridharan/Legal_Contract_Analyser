import re
from typing import Any, Dict, List


# ============================================================
# RISK CONFIGURATION
# ============================================================

# Base risk scores for CUAD categories.
#
# These are starting-point scores. The actual final score
# can be increased/decreased based on the language found
# inside the extracted clause.

CATEGORY_RISK = {

    # HIGH RISK
    "Uncapped Liability": 90,
    "Non-Compete": 85,
    "Ip Ownership Assignment": 85,
    "Termination For Convenience": 80,
    "Liquidated Damages": 80,
    "Anti-Assignment": 75,
    "Change Of Control": 75,
    "Irrevocable Or Perpetual License": 80,
    "Unlimited/All-You-Can-Eat-License": 75,

    # MEDIUM-HIGH RISK
    "Cap On Liability": 70,
    "Exclusivity": 70,
    "Non-Transferable License": 65,
    "Minimum Commitment": 65,
    "Most Favored Nation": 65,
    "Revenue/Profit Sharing": 65,
    "No-Solicit Of Customers": 65,
    "No-Solicit Of Employees": 65,
    "Covenant Not To Sue": 65,
    "Post-Termination Services": 65,
    "Rofr/Rofo/Rofn": 60,
    "Price Restrictions": 60,
    "Volume Restriction": 60,

    # MEDIUM RISK
    "License Grant": 55,
    "Joint Ip Ownership": 55,
    "Affiliate License-Licensee": 50,
    "Affiliate License-Licensor": 50,
    "Audit Rights": 50,
    "Insurance": 50,
    "Warranty Duration": 50,
    "Notice Period To Terminate Renewal": 50,
    "Renewal Term": 45,
    "Competitive Restriction Exception": 45,
    "Third Party Beneficiary": 45,

    # LOW-MEDIUM RISK
    "Governing Law": 35,
    "Effective Date": 20,
    "Expiration Date": 30,
    "Agreement Date": 15,
    "Document Name": 5,
    "Parties": 10,

    # SPECIAL CASE
    "Source Code Escrow": 60,
}


# ============================================================
# KEYWORD RULES
# ============================================================

RISK_KEYWORDS = {

    "high": [
        "uncapped",
        "unlimited liability",
        "without limitation",
        "sole discretion",
        "terminate immediately",
        "terminate at any time",
        "indemnify",
        "indemnification",
        "penalty",
        "liquidated damages",
        "perpetual",
        "irrevocable",
        "exclusive",
        "non-compete",
        "unlimited",
        "all liability",
    ],

    "medium": [
        "30 days",
        "60 days",
        "90 days",
        "notice",
        "renewal",
        "termination",
        "restriction",
        "consent",
        "approval",
        "audit",
        "insurance",
        "warranty",
        "confidential",
        "assignment",
    ],
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(text: Any) -> str:
    """
    Convert any input into normalized text.
    """

    if text is None:
        return ""

    text = str(text)

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def risk_level(score: int) -> str:
    """
    Convert numerical score into a risk level.
    """

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def get_category_base_score(
    category: str
) -> int:
    """
    Get the default score for a CUAD category.
    """

    category_normalized = normalize_text(
        category
    )

    for known_category, score in CATEGORY_RISK.items():

        if normalize_text(
            known_category
        ) == category_normalized:

            return score

    return 30


def find_keyword_matches(
    clause_text: str
) -> Dict[str, List[str]]:
    """
    Find risk-related keywords inside a clause.
    """

    text = normalize_text(
        clause_text
    )

    matches = {
        "high": [],
        "medium": []
    }

    for keyword in RISK_KEYWORDS["high"]:

        if keyword in text:

            matches["high"].append(
                keyword
            )

    for keyword in RISK_KEYWORDS["medium"]:

        if keyword in text:

            matches["medium"].append(
                keyword
            )

    return matches


# ============================================================
# NOTICE PERIOD ANALYSIS
# ============================================================

def analyze_notice_period(
    clause_text: str
) -> int:
    """
    Short termination/notice periods can increase risk.

    Returns an additional score.
    """

    text = normalize_text(
        clause_text
    )

    matches = re.findall(
        r"(\d+)\s*(day|days|month|months|year|years)",
        text
    )

    additional_score = 0

    for number, unit in matches:

        number = int(number)

        if "day" in unit:

            if number <= 15:
                additional_score += 15

            elif number <= 30:
                additional_score += 10

        elif "month" in unit:

            if number <= 1:
                additional_score += 10

        elif "year" in unit:

            if number <= 1:
                additional_score += 5

    return additional_score


# ============================================================
# LIABILITY ANALYSIS
# ============================================================

def analyze_liability(
    clause_text: str
) -> int:
    """
    Additional risk for liability language.
    """

    text = normalize_text(
        clause_text
    )

    score = 0

    if "uncapped" in text:
        score += 20

    if "unlimited liability" in text:
        score += 20

    if "without limitation" in text:
        score += 15

    if "indemnify" in text:
        score += 10

    if "indemnification" in text:
        score += 10

    if "maximum liability" in text:
        score -= 10

    if "liability shall not exceed" in text:
        score -= 10

    return score


# ============================================================
# TERMINATION ANALYSIS
# ============================================================
def analyze_termination(clause_text: str) -> int:
    """
    Additional risk for termination clauses.
    """

    text = normalize_text(clause_text)

    score = 0

    if "terminate at any time" in text:
        score += 20

    if "terminate immediately" in text:
        score += 20

    if "without cause" in text:
        score += 15

    if "sole discretion" in text:
        score += 15

    if "without notice" in text:
        score += 20

    if "written notice" in text:
        score += 5

    # Explicitly recognize short notice periods
    match = re.search(
        r"(\d+)\s*(day|days)",
        text
    )

    if match:

        days = int(match.group(1))

        if days <= 15:
            score += 15

        elif days <= 30:
            score += 10

    return score
# ============================================================
# REASON GENERATOR
# ============================================================

def generate_reason(
    category: str,
    clause_text: str,
    score: int,
    keyword_matches: Dict[str, List[str]]
) -> str:
    """
    Generate a human-readable explanation.
    """

    reasons = []

    # Category-based explanation
    if category in [
        "Uncapped Liability",
        "Cap On Liability"
    ]:

        reasons.append(
            "The clause affects the financial exposure "
            "of a contracting party."
        )

    elif category in [
        "Termination For Convenience"
    ]:

        reasons.append(
            "The clause controls whether a party can "
            "terminate the agreement without cause."
        )

    elif category in [
        "Non-Compete",
        "Exclusivity"
    ]:

        reasons.append(
            "The clause restricts the party's ability "
            "to conduct business with other parties."
        )

    elif category in [
        "Ip Ownership Assignment"
    ]:

        reasons.append(
            "The clause affects ownership or transfer "
            "of intellectual property rights."
        )

    elif category in [
        "Liquidated Damages"
    ]:

        reasons.append(
            "The clause may create a predefined "
            "financial consequence for breach or termination."
        )

    elif category in [
        "Anti-Assignment",
        "Change Of Control"
    ]:

        reasons.append(
            "The clause can restrict transfer of rights "
            "or changes in control of a contracting party."
        )

    elif category in [
        "Minimum Commitment",
        "Revenue/Profit Sharing",
        "Price Restrictions",
        "Volume Restriction"
    ]:

        reasons.append(
            "The clause creates a commercial or "
            "financial commitment."
        )

    elif category in [
        "Warranty Duration"
    ]:

        reasons.append(
            "The clause defines the duration of "
            "warranty-related obligations."
        )

    elif category in [
        "Governing Law"
    ]:

        reasons.append(
            "The clause determines which jurisdiction's "
            "law governs the agreement."
        )

    else:

        reasons.append(
            "The clause contains contractual obligations "
            "that may require legal review."
        )

    # Keyword evidence
    if keyword_matches["high"]:

        keywords = ", ".join(
            keyword_matches["high"]
        )

        reasons.append(
            f"Risk-related language detected: {keywords}."
        )

    elif keyword_matches["medium"]:

        keywords = ", ".join(
            keyword_matches["medium"]
        )

        reasons.append(
            f"Relevant contractual language detected: {keywords}."
        )

    # Notice-period evidence
    notice_score = analyze_notice_period(
        clause_text
    )

    if notice_score > 0:

        reasons.append(
            "The notice period may create additional "
            "timing risk."
        )

    return " ".join(
        reasons
    )


# ============================================================
# SCORE ONE CLAUSE
# ============================================================

def score_clause(
    category: str,
    clause_text: str
) -> Dict[str, Any]:
    """
    Calculate risk for one extracted clause.
    """

    category = str(
        category
    ).strip()

    clause_text = str(
        clause_text
    ).strip()

    base_score = get_category_base_score(
        category
    )

    keyword_matches = find_keyword_matches(
        clause_text
    )

    score = base_score

    # High-risk keywords
    score += (
        len(
            keyword_matches["high"]
        ) * 5
    )

    # Medium-risk keywords
    score += (
        len(
            keyword_matches["medium"]
        ) * 2
    )

    # Notice period
    score += analyze_notice_period(
        clause_text
    )

    # Liability-specific rules
    if "liability" in normalize_text(
        category
    ):

        score += analyze_liability(
            clause_text
        )

    # Termination-specific rules
    if "termination" in normalize_text(
        category
    ):

        score += analyze_termination(
            clause_text
        )

    # Keep score within 0-100
    score = max(
        0,
        min(
            100,
            score
        )
    )

    level = risk_level(
        score
    )

    reason = generate_reason(
        category,
        clause_text,
        score,
        keyword_matches
    )

    return {

        "category": category,

        "clause": clause_text,

        "risk_score": score,

        "risk_level": level,

        "reason": reason,

        "risk_indicators": {
            "high": keyword_matches["high"],
            "medium": keyword_matches["medium"]
        }
    }


# ============================================================
# NORMALIZE CLAUSE INPUT
# ============================================================

def normalize_clauses(
    clauses: Any
) -> List[Dict[str, str]]:
    """
    Accept several possible formats from your
    existing clause extractor.
    """

    normalized = []

    # --------------------------------------------------------
    # Format:
    #
    # {
    #   "Termination": "...",
    #   "Governing Law": "..."
    # }
    # --------------------------------------------------------

    if isinstance(
        clauses,
        dict
    ):

        # If response contains "clauses"
        if "clauses" in clauses:

            return normalize_clauses(
                clauses["clauses"]
            )

        for category, value in clauses.items():

            if isinstance(
                value,
                list
            ):

                for item in value:

                    if isinstance(
                        item,
                        dict
                    ):

                        text = (
                            item.get("text")
                            or item.get("clause")
                            or item.get("content")
                        )

                    else:

                        text = item

                    if text:

                        normalized.append({
                            "category": str(
                                category
                            ),
                            "text": str(
                                text
                            )
                        })

            elif isinstance(
                value,
                str
            ):

                normalized.append({
                    "category": str(
                        category
                    ),
                    "text": value
                })

        return normalized

    # --------------------------------------------------------
    # Format:
    #
    # [
    #   {
    #      "category": "Termination",
    #      "text": "..."
    #   }
    # ]
    # --------------------------------------------------------

    if isinstance(
        clauses,
        list
    ):

        for item in clauses:

            if not isinstance(
                item,
                dict
            ):

                continue

            category = (
                item.get("category")
                or item.get("type")
                or item.get("name")
            )

            text = (
                item.get("text")
                or item.get("clause")
                or item.get("content")
            )

            if category and text:

                normalized.append({
                    "category": str(
                        category
                    ),
                    "text": str(
                        text
                    )
                })

    return normalized


# ============================================================
# SCORE ALL CLAUSES
# ============================================================

def score_contract(
    clauses: Any
) -> Dict[str, Any]:
    """
    Score every extracted clause.
    """

    normalized = normalize_clauses(
        clauses
    )

    results = []

    for clause in normalized:

        result = score_clause(
            clause["category"],
            clause["text"]
        )

        results.append(
            result
        )

    # Sort highest risk first
    results.sort(
        key=lambda x: x["risk_score"],
        reverse=True
    )

    # Summary
    high_count = sum(
        1
        for item in results
        if item["risk_level"] == "HIGH"
    )

    medium_count = sum(
        1
        for item in results
        if item["risk_level"] == "MEDIUM"
    )

    low_count = sum(
        1
        for item in results
        if item["risk_level"] == "LOW"
    )

    if results:

        overall_score = round(
            sum(
                item["risk_score"]
                for item in results
            )
            / len(results)
        )

    else:

        overall_score = 0

    return {

        "overall_risk_score":
            overall_score,

        "overall_risk_level":
            risk_level(
                overall_score
            ),

        "summary": {
            "total_clauses":
                len(results),

            "high_risk":
                high_count,

            "medium_risk":
                medium_count,

            "low_risk":
                low_count
        },

        "risks":
            results
    }