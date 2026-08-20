import json
import csv
import re
import time
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CUAD_FILE = BASE_DIR / "app" / "evaluation" / "cuad.json"

RESULTS_DIR = BASE_DIR / "app" / "evaluation" / "results"
PREDICTIONS_FILE = RESULTS_DIR / "cuad_predictions.json"

FINAL_JSON = RESULTS_DIR / "cuad_evaluation.json"
FINAL_CSV = RESULTS_DIR / "cuad_evaluation.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

NUM_CONTRACTS = 5

MATCH_THRESHOLD = 0.70


# ============================================================
# CUAD 41 CATEGORIES
# ============================================================

CUAD_CATEGORIES = [
    "Affiliate License-Licensee",
    "Affiliate License-Licensor",
    "Agreement Date",
    "Anti-Assignment",
    "Audit Rights",
    "Cap On Liability",
    "Change Of Control",
    "Competitive Restriction Exception",
    "Covenant Not To Sue",
    "Document Name",
    "Effective Date",
    "Exclusivity",
    "Expiration Date",
    "Governing Law",
    "Insurance",
    "Ip Ownership Assignment",
    "Irrevocable Or Perpetual License",
    "Joint Ip Ownership",
    "License Grant",
    "Liquidated Damages",
    "Minimum Commitment",
    "Most Favored Nation",
    "No-Solicit Of Customers",
    "No-Solicit Of Employees",
    "Non-Compete",
    "Non-Disparagement",
    "Non-Transferable License",
    "Notice Period To Terminate Renewal",
    "Parties",
    "Post-Termination Services",
    "Price Restrictions",
    "Renewal Term",
    "Revenue/Profit Sharing",
    "Rofr/Rofo/Rofn",
    "Source Code Escrow",
    "Termination For Convenience",
    "Third Party Beneficiary",
    "Uncapped Liability",
    "Unlimited/All-You-Can-Eat-License",
    "Volume Restriction",
    "Warranty Duration",
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = text.replace("“", '"')
    text = text.replace("”", '"')
    text = text.replace("‘", "'")
    text = text.replace("’", "'")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text):

    return re.findall(
        r"\b\w+\b",
        normalize_text(text)
    )


# ============================================================
# SIMILARITY
# ============================================================

def similarity(text1, text2):

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0.0

    return SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()


# ============================================================
# TOKEN PRECISION / RECALL / F1
# ============================================================

def token_precision_recall_f1(
    prediction,
    ground_truth
):

    pred_tokens = tokenize(prediction)
    truth_tokens = tokenize(ground_truth)

    if not pred_tokens and not truth_tokens:
        return 1.0, 1.0, 1.0

    if not pred_tokens:
        return 0.0, 0.0, 0.0

    if not truth_tokens:
        return 0.0, 0.0, 0.0

    pred_counts = defaultdict(int)

    for token in pred_tokens:
        pred_counts[token] += 1

    truth_counts = defaultdict(int)

    for token in truth_tokens:
        truth_counts[token] += 1

    common = 0

    for token in pred_counts:

        if token in truth_counts:

            common += min(
                pred_counts[token],
                truth_counts[token]
            )

    precision = common / len(pred_tokens)

    recall = common / len(truth_tokens)

    if precision + recall == 0:

        f1 = 0.0

    else:

        f1 = (
            2 * precision * recall
            / (precision + recall)
        )

    return precision, recall, f1


# ============================================================
# CUAD CATEGORY DETECTION
# ============================================================

def get_category(question):

    question_lower = question.lower()

    for category in CUAD_CATEGORIES:

        if category.lower() in question_lower:

            return category

    return question.strip()


# ============================================================
# LOAD CUAD
# ============================================================

def load_cuad():

    if not CUAD_FILE.exists():

        raise FileNotFoundError(
            f"\nCUAD dataset not found:\n"
            f"{CUAD_FILE}"
        )

    with open(
        CUAD_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# EXTRACT CUAD GROUND TRUTH
# ============================================================

def extract_ground_truth(contract):

    ground_truth = {}

    for paragraph in contract.get(
        "paragraphs",
        []
    ):

        for qa in paragraph.get(
            "qas",
            []
        ):

            question = qa.get(
                "question",
                ""
            )

            category = get_category(
                question
            )

            answers = qa.get(
                "answers",
                []
            )

            answer_texts = []

            for answer in answers:

                text = answer.get(
                    "text",
                    ""
                )

                if text:

                    answer_texts.append(
                        text
                    )

            ground_truth[category] = (
                answer_texts
            )

    return ground_truth


# ============================================================
# CONTRACT TEXT
# ============================================================

def get_contract_text(contract):

    return "\n".join(
        paragraph.get(
            "context",
            ""
        )
        for paragraph in contract.get(
            "paragraphs",
            []
        )
    )


# ============================================================
# RUN EXISTING EXTRACTOR
# ============================================================

def run_your_extractor(contract_text):

    try:

        from app.nlp.clause_extractor import (
            extract_clauses
        )

    except ImportError as e:

        print("\nERROR importing clause extractor:")
        print(e)

        raise

    return extract_clauses(
        contract_text
    )


# ============================================================
# NORMALIZE PREDICTIONS
# ============================================================

def normalize_predictions(predictions):

    normalized = {}

    if predictions is None:

        return normalized

    # --------------------------------------------------------
    # Case 1:
    # {
    #   "Termination": "...",
    #   "Governing Law": "..."
    # }
    # --------------------------------------------------------

    if isinstance(
        predictions,
        dict
    ):

        # Handle {"clauses": [...]}
        if "clauses" in predictions:

            clauses = predictions[
                "clauses"
            ]

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
                        item.get(
                            "category"
                        )
                        or item.get(
                            "type"
                        )
                        or item.get(
                            "name"
                        )
                    )

                    text = (
                        item.get(
                            "text"
                        )
                        or item.get(
                            "clause"
                        )
                        or item.get(
                            "content"
                        )
                    )

                    if category and text:

                        normalized.setdefault(
                            str(category).strip(),
                            []
                        ).append(
                            str(text)
                        )

                return normalized

        # Normal dictionary format
        for category, value in predictions.items():

            category = str(
                category
            ).strip()

            if category not in CUAD_CATEGORIES:

                # Try to map category name
                for cuad_category in CUAD_CATEGORIES:

                    if (
                        cuad_category.lower()
                        == category.lower()
                    ):

                        category = cuad_category

                        break

            if isinstance(
                value,
                list
            ):

                clauses = [
                    str(x)
                    for x in value
                    if x
                ]

            elif isinstance(
                value,
                str
            ):

                clauses = [value]

            elif isinstance(
                value,
                dict
            ):

                text = (
                    value.get("text")
                    or value.get("clause")
                    or value.get("content")
                )

                clauses = (
                    [str(text)]
                    if text
                    else []
                )

            else:

                clauses = []

            if clauses:

                normalized[
                    category
                ] = clauses

        return normalized

    return normalized


# ============================================================
# LOAD SAVED PREDICTIONS
# ============================================================

def load_saved_predictions():

    if not PREDICTIONS_FILE.exists():

        return {}

    with open(
        PREDICTIONS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# SAVE PREDICTIONS IMMEDIATELY
# ============================================================

def save_predictions(
    predictions
):

    with open(
        PREDICTIONS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            predictions,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# FIND BEST PREDICTION
# ============================================================

def find_best_prediction(
    predictions,
    ground_truth_answers
):

    best_prediction = ""

    best_score = 0.0

    for prediction in predictions:

        for truth in ground_truth_answers:

            score = similarity(
                prediction,
                truth
            )

            if score > best_score:

                best_score = score

                best_prediction = prediction

    return (
        best_prediction,
        best_score
    )


# ============================================================
# EVALUATE CATEGORY
# ============================================================

def evaluate_category(
    predictions,
    ground_truth_answers
):

    # Ground truth exists but no prediction
    if not predictions:

        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "matched": False,
            "similarity": 0.0
        }

    # Prediction exists but no ground truth
    if not ground_truth_answers:

        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "matched": False,
            "similarity": 0.0
        }

    best_prediction, best_similarity = (
        find_best_prediction(
            predictions,
            ground_truth_answers
        )
    )

    if best_similarity >= MATCH_THRESHOLD:

        precision, recall, f1 = (
            token_precision_recall_f1(
                best_prediction,
                ground_truth_answers[0]
            )
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "matched": True,
            "similarity": best_similarity
        }

    return {
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "matched": False,
        "similarity": best_similarity
    }


# ============================================================
# EVALUATE ONE CONTRACT
# ============================================================

def evaluate_contract(
    contract,
    prediction
):

    title = contract.get(
        "title",
        "Unknown Contract"
    )

    ground_truth = extract_ground_truth(
        contract
    )

    predictions = normalize_predictions(
        prediction
    )

    category_results = {}

    for category in CUAD_CATEGORIES:

        answers = ground_truth.get(
            category,
            []
        )

        predicted = predictions.get(
            category,
            []
        )

        category_results[
            category
        ] = {
            "ground_truth": answers,
            "prediction": predicted,
            **evaluate_category(
                predicted,
                answers
            )
        }

    return {
        "contract": title,
        "categories": category_results
    }


# ============================================================
# CALCULATE OVERALL RESULTS
# ============================================================

def calculate_overall(
    all_results
):

    precision_values = []
    recall_values = []
    f1_values = []

    category_scores = defaultdict(list)

    for contract_result in all_results:

        for category, result in (
            contract_result[
                "categories"
            ].items()
        ):

            precision_values.append(
                result["precision"]
            )

            recall_values.append(
                result["recall"]
            )

            f1_values.append(
                result["f1"]
            )

            category_scores[
                category
            ].append(
                result["f1"]
            )

    overall_precision = (
        sum(precision_values)
        / len(precision_values)
        if precision_values
        else 0
    )

    overall_recall = (
        sum(recall_values)
        / len(recall_values)
        if recall_values
        else 0
    )

    overall_f1 = (
        sum(f1_values)
        / len(f1_values)
        if f1_values
        else 0
    )

    per_category = {}

    for category, scores in (
        category_scores.items()
    ):

        per_category[category] = (
            sum(scores)
            / len(scores)
        )

    return {
        "overall": {
            "precision": overall_precision,
            "recall": overall_recall,
            "f1": overall_f1
        },
        "per_category_f1": per_category
    }


# ============================================================
# SAVE FINAL JSON
# ============================================================

def save_final_json(
    all_results,
    overall_results,
    successful_count,
    failed_count
):

    output = {

        "contracts_requested": NUM_CONTRACTS,

        "contracts_successfully_evaluated":
            successful_count,

        "contracts_failed":
            failed_count,

        "overall_results":
            overall_results,

        "contract_results":
            all_results
    }

    with open(
        FINAL_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# SAVE FINAL CSV
# ============================================================

def save_final_csv(
    all_results
):

    rows = []

    for contract_result in all_results:

        contract = contract_result[
            "contract"
        ]

        for category, result in (
            contract_result[
                "categories"
            ].items()
        ):

            rows.append({

                "contract":
                    contract,

                "category":
                    category,

                "precision":
                    result["precision"],

                "recall":
                    result["recall"],

                "f1":
                    result["f1"],

                "matched":
                    result["matched"]
            })

    with open(
        FINAL_CSV,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "contract",
                "category",
                "precision",
                "recall",
                "f1",
                "matched"
            ]
        )

        writer.writeheader()

        writer.writerows(rows)


# ============================================================
# PRINT REPORT
# ============================================================

def print_report(
    all_results,
    overall_results,
    failed_count
):

    overall = overall_results[
        "overall"
    ]

    print("\n")

    print("=" * 70)
    print("CUAD EVALUATION RESULTS")
    print("=" * 70)

    print(
        f"\nContracts successfully evaluated: "
        f"{len(all_results)}"
    )

    print(
        f"Contracts failed/skipped: "
        f"{failed_count}"
    )

    print(
        f"\nPrecision : "
        f"{overall['precision']:.4f}"
    )

    print(
        f"Recall    : "
        f"{overall['recall']:.4f}"
    )

    print(
        f"F1 Score  : "
        f"{overall['f1']:.4f}"
    )

    print("\n" + "-" * 70)

    print("PER-CATEGORY F1")

    print("-" * 70)

    for category, f1 in sorted(
        overall_results[
            "per_category_f1"
        ].items()
    ):

        print(
            f"{category:<50} "
            f"{f1:.4f}"
        )

    print("=" * 70)

    print(
        f"\nResults saved to:\n"
        f"{FINAL_JSON}\n"
        f"{FINAL_CSV}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CUAD CONTRACT CLAUSE EVALUATOR")
    print("=" * 70)

    dataset = load_cuad()

    contracts = dataset.get(
        "data",
        []
    )

    print(
        f"\nTotal contracts in dataset: "
        f"{len(contracts)}"
    )

    selected_contracts = contracts[
        :NUM_CONTRACTS
    ]

    print(
        f"Contracts selected for evaluation: "
        f"{len(selected_contracts)}"
    )

    # --------------------------------------------------------
    # Load existing predictions
    # --------------------------------------------------------

    saved_predictions = (
        load_saved_predictions()
    )

    print(
        f"Previously saved predictions: "
        f"{len(saved_predictions)}"
    )

    # --------------------------------------------------------
    # Generate missing predictions
    # --------------------------------------------------------

    for index, contract in enumerate(
        selected_contracts,
        start=1
    ):

        title = contract.get(
            "title",
            f"Contract {index}"
        )

        print("\n" + "=" * 70)

        print(
            f"Contract {index}/{len(selected_contracts)}"
        )

        print(title)

        print("=" * 70)

        # Already processed
        if title in saved_predictions:

            print(
                "Prediction already saved."
            )

            print(
                "Skipping Gemini API call."
            )

            continue

        contract_text = get_contract_text(
            contract
        )

        try:

            print(
                "Calling clause extractor..."
            )

            prediction = run_your_extractor(
                contract_text
            )

            prediction = normalize_predictions(
                prediction
            )

            saved_predictions[
                title
            ] = prediction

            # SAVE IMMEDIATELY
            save_predictions(
                saved_predictions
            )

            print(
                f"Prediction saved."
            )

            print(
                f"Predicted categories: "
                f"{len(prediction)}"
            )

        except Exception as e:

            print(
                "\nERROR:"
            )

            print(e)

            # Save whatever we already have
            save_predictions(
                saved_predictions
            )

            print(
                "\nStopping evaluation."
            )

            print(
                "Run the same command later "
                "to resume."
            )

            break

    # --------------------------------------------------------
    # Evaluate all saved predictions
    # --------------------------------------------------------

    all_results = []

    failed_count = 0

    for contract in selected_contracts:

        title = contract.get(
            "title",
            "Unknown Contract"
        )

        if title not in saved_predictions:

            failed_count += 1

            continue

        result = evaluate_contract(
            contract,
            saved_predictions[title]
        )

        all_results.append(
            result
        )

    # --------------------------------------------------------
    # Nothing available yet
    # --------------------------------------------------------

    if not all_results:

        print(
            "\nNo contracts were successfully "
            "evaluated yet."
        )

        print(
            "\nYour Gemini quota may be exhausted."
        )

        print(
            "Run this command again after "
            "the quota resets:"
        )

        print(
            "\npython -m app.evaluation.evaluate_cuad"
        )

        return

    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------

    overall_results = calculate_overall(
        all_results
    )

    print_report(
        all_results,
        overall_results,
        failed_count
    )

    save_final_json(
        all_results,
        overall_results,
        len(all_results),
        failed_count
    )

    save_final_csv(
        all_results
    )


if __name__ == "__main__":
    main()