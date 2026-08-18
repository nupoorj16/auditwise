"""
Runs the eval set end-to-end through the real pipeline (filter extraction ->
structured filtering/aggregation -> generation) and checks results against
independently-computed expected values. Prints a pass/fail report and saves
it to eval/eval_report.json.
"""
import json
from src.retrieval import load_data
from src.generation import answer_question
from eval.eval_set import USER_ID, CASES


def check_case(case: dict, retrieval: dict) -> tuple[bool, str]:
    if case["check"] == "aggregate":
        actual = retrieval["aggregate"]
        tol = case.get("tol", 0.01)
        if actual is None:
            return False, "expected an aggregate, got None"
        passed = abs(actual - case["expected"]) <= tol
        return passed, f"expected {case['expected']}, got {actual}"

    if case["check"] == "matched_count":
        actual = retrieval["matched_count"]
        passed = actual == case["expected"]
        return passed, f"expected {case['expected']}, got {actual}"

    if case["check"] == "lookup":
        rows = retrieval["context_rows"]
        if len(rows) != 1:
            return False, f"expected exactly 1 matching row, got {len(rows)}"
        row = rows.iloc[0]
        exp = case["expected"]
        passed = (
            row["transaction_id_clean"] == exp["transaction_id_clean"]
            and abs(row["amount_clean"] - exp["amount_clean"]) <= 0.01
        )
        return passed, f"expected {exp}, got transaction_id={row['transaction_id_clean']} amount={row['amount_clean']}"

    raise ValueError(f"Unknown check type: {case['check']}")


if __name__ == "__main__":
    df = load_data()
    results = []
    n_passed = 0

    for case in CASES:
        result = answer_question(case["question"], USER_ID, df)
        retrieval = result["retrieval"]
        passed, detail = check_case(case, retrieval)
        n_passed += passed

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] #{case['id']}: {case['question']}")
        print(f"       {detail}")
        print(f"       answer: {result['answer']}")
        print()

        results.append({
            "id": case["id"],
            "question": case["question"],
            "check": case["check"],
            "passed": bool(passed),
            "detail": detail,
            "filters": retrieval["filters"],
            "answer": result["answer"],
        })

    print(f"Score: {n_passed}/{len(CASES)} passed")

    with open("eval/eval_report.json", "w") as f:
        json.dump({"score": f"{n_passed}/{len(CASES)}", "results": results}, f, indent=2)
    print("Saved to eval/eval_report.json")
