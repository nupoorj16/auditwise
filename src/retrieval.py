"""
Step: hybrid retrieval - turn a natural language question into structured
filters (via an LLM tool call), apply them to the cleaned dataframe,
compute any aggregate in code, and fall back to semantic search over
Chroma for free-text/descriptive parts of the question.

user_id is always passed in by the caller, never inferred from the
question text - retrieval must never be able to leak one user's data
into another user's answer.
"""
import json
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from src.embed_and_store import get_collection

load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"


def load_data(path="data/processed/combined_chunked.csv") -> pd.DataFrame:
    """Load cleaned transaction data with date_clean as a real datetime column."""
    df = pd.read_csv(path)
    df["date_clean"] = pd.to_datetime(df["date_clean"], errors="coerce")
    return df

CANONICAL_CATEGORIES = [
    "Food", "Rent", "Travel", "Utilities", "Entertainment",
    "Bonus", "Salary", "Others", "Other Income", "Savings",
    "Education", "Health", "Freelance", "Investment",
]

EXTRACT_FILTERS_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_filters",
        "description": "Extract structured filters from a natural language question about personal finance transactions.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": ["string", "null"], "description": "ISO date YYYY-MM-DD, inclusive start of date range, or null if not specified"},
                "end_date": {"type": ["string", "null"], "description": "ISO date YYYY-MM-DD, inclusive end of date range, or null if not specified"},
                "category": {"type": ["string", "null"], "enum": CANONICAL_CATEGORIES + [None]},
                "anomalies_only": {"type": "boolean", "description": "true if the question is asking about suspicious/unusual/flagged transactions"},
                "aggregation": {"type": "string", "enum": ["sum", "average", "count", "none"]},
                "aggregation_period": {"type": ["string", "null"], "enum": ["monthly", "total", None], "description": "'monthly' for questions like 'average monthly spend', 'total' for a single sum/average/count over the whole range, null if aggregation is 'none'"},
                "semantic_terms": {"type": ["string", "null"], "description": "Leftover descriptive keywords (e.g. a merchant or description mentioned) for semantic search over transaction notes. Null if the question is purely structured (dates/category/aggregation)."},
            },
            "required": ["start_date", "end_date", "category", "anomalies_only", "aggregation", "aggregation_period", "semantic_terms"],
        },
    },
}


def extract_filters(question: str, reference_today: str) -> dict:
    system_prompt = (
        f"Today's date is {reference_today}. Resolve relative dates ('this month', 'last month', "
        "'in March 2022') against that date. Extract structured filters from the user's question "
        "about their personal finance transactions."
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        tools=[EXTRACT_FILTERS_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_filters"}},
    )
    tool_call = response.choices[0].message.tool_calls[0]
    return json.loads(tool_call.function.arguments)


def apply_structured_filters(df: pd.DataFrame, user_id: str, filters: dict) -> pd.DataFrame:
    mask = df["user_id"] == user_id
    if filters.get("start_date"):
        mask &= df["date_clean"] >= pd.Timestamp(filters["start_date"])
    if filters.get("end_date"):
        mask &= df["date_clean"] <= pd.Timestamp(filters["end_date"])
    if filters.get("category"):
        mask &= df["category_clean"] == filters["category"]
    if filters.get("anomalies_only"):
        mask &= df["is_anomaly"] == True  # noqa: E712
    return df[mask]


def compute_aggregate(filtered_df: pd.DataFrame, filters: dict):
    agg = filters.get("aggregation", "none")
    if agg == "none" or len(filtered_df) == 0:
        return None

    if filters.get("aggregation_period") == "monthly":
        monthly = filtered_df.groupby(filtered_df["date_clean"].dt.strftime("%Y-%m"))["amount_clean"].sum()
        if agg == "average":
            return round(monthly.mean(), 2)
        if agg == "sum":
            return round(monthly.sum(), 2)
        return int(monthly.count())  # number of distinct months

    if agg == "sum":
        return round(filtered_df["amount_clean"].sum(), 2)
    if agg == "average":
        return round(filtered_df["amount_clean"].mean(), 2)
    return int(len(filtered_df))


def semantic_search(query: str, filters: dict, user_id: str, n_results=10) -> pd.DataFrame:
    collection = get_collection()
    where_clauses = [{"user_id": user_id}]
    if filters.get("category"):
        where_clauses.append({"category": filters["category"]})
    if filters.get("anomalies_only"):
        where_clauses.append({"is_anomaly": True})
    where = {"$and": where_clauses} if len(where_clauses) > 1 else where_clauses[0]

    result = collection.query(query_texts=[query], n_results=n_results, where=where)
    rows = result["metadatas"][0]
    docs = result["documents"][0]

    hits = pd.DataFrame(rows)
    hits["chunk_text"] = docs
    if len(hits) == 0:
        return hits

    # Chroma's `where` can't cleanly do string date-range comparisons,
    # so enforce the date range here in pandas instead.
    if filters.get("start_date"):
        hits = hits[hits["date"] >= filters["start_date"]]
    if filters.get("end_date"):
        hits = hits[hits["date"] <= filters["end_date"]]
    return hits


def retrieve(question: str, user_id: str, df: pd.DataFrame) -> dict:
    reference_today = df["date_clean"].max().strftime("%Y-%m-%d")
    filters = extract_filters(question, reference_today)

    structured_df = apply_structured_filters(df, user_id, filters)
    aggregate = compute_aggregate(structured_df, filters)

    if filters.get("semantic_terms"):
        context_rows = semantic_search(filters["semantic_terms"], filters, user_id)
    elif filters.get("aggregation", "none") != "none":
        context_rows = structured_df.head(5)[["transaction_id_clean", "date_clean", "category_clean", "amount_clean", "chunk_text"]]
    else:
        context_rows = structured_df.head(15)[["transaction_id_clean", "date_clean", "category_clean", "amount_clean", "chunk_text"]]

    return {
        "filters": filters,
        "reference_today": reference_today,
        "aggregate": aggregate,
        "matched_count": len(structured_df),
        "context_rows": context_rows,
    }


if __name__ == "__main__":
    df = load_data()

    sample_user = df["user_id"].value_counts().idxmax()
    print("Testing retrieval for user:", sample_user)
    print()

    test_questions = [
        "How much did I spend on food in March 2022?",
        "What's my average monthly subscription spend?",
        "What transactions look suspicious this month?",
    ]

    for q in test_questions:
        print("Q:", q)
        result = retrieve(q, sample_user, df)
        print("  filters:", result["filters"])
        print("  matched_count:", result["matched_count"])
        print("  aggregate:", result["aggregate"])
        print("  context rows:", len(result["context_rows"]))
        print()
