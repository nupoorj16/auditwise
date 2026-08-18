"""
Step: turn a retrieval result into a natural-language, cited answer.

The LLM never computes numbers itself - aggregates are precomputed in
retrieval.py and handed over as a fact to state, not a value to derive.
"""
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from src.retrieval import retrieve, load_data

load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a personal finance assistant. Answer the user's question about \
their own transactions using ONLY the data provided below - never invent transactions, \
amounts, or dates that aren't given to you.

Rules:
- If a precomputed aggregate value is given, state it exactly as given. Do not recompute \
it yourself from the listed transactions (the list may only be a sample, not the full set).
- When you reference a specific transaction, cite its transaction ID in parentheses, e.g. (A_T4325).
- If no transactions matched, say so plainly rather than guessing.
- For anomaly/flagged-transaction questions, explain using the given category median and \
normal range (lower_bound/upper_bound) - e.g. "typical Food spending is around $X, but this was $Y."
- Keep answers concise and concrete, grounded in the numbers given.
"""


def format_context(result: dict) -> str:
    lines = []
    if result["aggregate"] is not None:
        lines.append(f"Precomputed aggregate answer: {result['aggregate']}")
    lines.append(f"Number of matching transactions: {result['matched_count']}")
    lines.append("")

    rows = result["context_rows"]
    if len(rows) == 0:
        lines.append("No individual transactions to list.")
        return "\n".join(lines)

    lines.append("Relevant transactions:")
    for _, row in rows.iterrows():
        date = row.get("date_clean")
        date_str = date.strftime("%Y-%m-%d") if pd.notna(date) else "unknown date"
        amount = row.get("amount_clean")
        amount_str = f"${amount:,.2f}" if pd.notna(amount) else "unknown amount"
        line = f"- [{row.get('transaction_id_clean')}] {date_str} | {row.get('category_clean')} | {amount_str}"
        if row.get("is_anomaly"):
            lb, ub, med = row.get("lower_bound"), row.get("upper_bound"), row.get("category_median")
            line += f" | FLAGGED (category typical range ${lb:,.2f} to ${ub:,.2f}, median ${med:,.2f})"
        lines.append(line)
    return "\n".join(lines)


def answer_question(question: str, user_id: str, df: pd.DataFrame) -> dict:
    result = retrieve(question, user_id, df)
    context = format_context(result)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nData:\n{context}"},
        ],
    )

    return {
        "question": question,
        "answer": response.choices[0].message.content,
        "retrieval": result,
    }


if __name__ == "__main__":
    df = load_data()
    sample_user = df["user_id"].value_counts().idxmax()
    print("Testing generation for user:", sample_user)
    print()

    test_questions = [
        "How much have I spent on food overall?",
        "What transactions look suspicious or unusual?",
        "Why was transaction A_T4325 flagged?",
    ]

    for q in test_questions:
        result = answer_question(q, sample_user, df)
        print("Q:", q)
        print("A:", result["answer"])
        print()
