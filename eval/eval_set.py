"""
Eval set: 18 question/answer pairs against a fixed demo user (A_U036),
with expected values computed independently in pandas (see the ground-truth
queries this was derived from in the project history) - not derived from
the pipeline itself, so this actually tests correctness rather than
circularity.

Each case checks one of:
- "aggregate": retrieval['aggregate'] should equal `expected` (within `tol`)
- "matched_count": retrieval['matched_count'] should equal `expected`
- "lookup": retrieval['context_rows'] should contain exactly one row
  matching `expected` (a dict with transaction_id_clean/amount_clean)
"""

USER_ID = "A_U036"

CASES = [
    {"id": 1, "question": "How much have I spent on Food overall?", "check": "aggregate", "expected": 88581.0},
    {"id": 2, "question": "How much have I spent on Rent overall?", "check": "aggregate", "expected": 242075.0},
    {"id": 3, "question": "How much have I spent on Travel overall?", "check": "aggregate", "expected": 100658.0},
    {"id": 4, "question": "How much have I spent on Entertainment overall?", "check": "aggregate", "expected": 39493.0},
    {"id": 5, "question": "How much have I spent on Education overall?", "check": "aggregate", "expected": 37262.0},
    {"id": 6, "question": "How much have I spent on Utilities overall?", "check": "aggregate", "expected": 49635.0},
    {"id": 7, "question": "How much have I spent on Savings overall?", "check": "aggregate", "expected": 6975.0},
    {"id": 8, "question": "What is my total income?", "check": "aggregate", "expected": 1118050.0},
    {"id": 19, "question": "What is my total spending across all categories?", "check": "aggregate", "expected": 589706.0},
    {"id": 9, "question": "How many transactions have I made in total?", "check": "matched_count", "expected": 131},
    {"id": 10, "question": "How much did I spend on Food in 2023?", "check": "aggregate", "expected": 32811.0},
    {"id": 11, "question": "What is my average Food transaction amount?", "check": "aggregate", "expected": 3280.78, "tol": 1.0},
    {"id": 12, "question": "What is my average Rent transaction amount?", "check": "aggregate", "expected": 12103.75, "tol": 1.0},
    {"id": 13, "question": "What is my average Health transaction amount?", "check": "aggregate", "expected": 5092.50, "tol": 1.0},
    # Expected is 21, not 20: one Rent row has a null amount_clean (it hit the
    # 999999999 sentinel and got nulled during cleaning), so a naive
    # pandas .agg('count') silently drops it. The transaction still happened.
    {"id": 14, "question": "How many Rent transactions have I made?", "check": "aggregate", "expected": 21},
    {"id": 15, "question": "How many of my transactions look suspicious or unusual?", "check": "matched_count", "expected": 6},
    {
        "id": 16,
        "question": "What are all my flagged Rent transactions?",
        "check": "matched_count",
        "expected": 4,
    },
    {
        "id": 17,
        "question": "Why was transaction A_T4325 flagged?",
        "check": "lookup",
        "expected": {"transaction_id_clean": "A_T4325", "amount_clean": 9606.0},
    },
    {
        "id": 18,
        "question": "Why was transaction A_T6360 flagged?",
        "check": "lookup",
        "expected": {"transaction_id_clean": "A_T6360", "amount_clean": 33185.0},
    },
]
