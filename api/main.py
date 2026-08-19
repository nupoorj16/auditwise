"""
FastAPI backend exposing the cleaning/anomaly/RAG pipeline in src/ as HTTP
endpoints for the Next.js frontend. Data is loaded once at startup and kept
in memory - fine at this scale (30K rows), avoids re-reading the CSV per request.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from src.retrieval import load_data
from src.generation import answer_question

app = FastAPI(title="Finance RAG API")

# CORS_ORIGINS is a comma-separated list, e.g. "https://my-app.vercel.app,http://localhost:3000"
_extra_origins = os.environ.get("CORS_ORIGINS", "")
allow_origins = ["http://localhost:3000"] + [o.strip() for o in _extra_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

DF = load_data()


def get_user_df(user_id: str) -> pd.DataFrame:
    user_df = DF[DF["user_id"] == user_id]
    if len(user_df) == 0:
        raise HTTPException(status_code=404, detail=f"Unknown user_id: {user_id}")
    return user_df


@app.get("/api/users")
def list_users(limit: int = 50):
    counts = DF["user_id"].value_counts().head(limit)
    return [{"user_id": uid, "transaction_count": int(n)} for uid, n in counts.items()]


@app.get("/api/users/{user_id}/summary")
def user_summary(user_id: str):
    user_df = get_user_df(user_id)
    expenses = user_df[user_df["transaction_type"] == "Expense"]
    income = user_df[user_df["transaction_type"] == "Income"]
    dates = user_df["date_clean"].dropna()

    return {
        "total_transactions": int(len(user_df)),
        "total_spend": round(float(expenses["amount_clean"].sum()), 2),
        "total_income": round(float(income["amount_clean"].sum()), 2),
        "anomalies_count": int(user_df["is_anomaly"].sum()),
        "date_range_start": dates.min().strftime("%Y-%m-%d") if len(dates) else None,
        "date_range_end": dates.max().strftime("%Y-%m-%d") if len(dates) else None,
    }


@app.get("/api/users/{user_id}/spend-by-category")
def spend_by_category(user_id: str):
    user_df = get_user_df(user_id)
    expenses = user_df[user_df["transaction_type"] == "Expense"]
    totals = expenses.groupby("category_clean")["amount_clean"].sum().sort_values(ascending=False)
    return [{"category": cat, "total": round(float(v), 2)} for cat, v in totals.items()]


@app.get("/api/users/{user_id}/anomalies")
def anomalies(user_id: str):
    user_df = get_user_df(user_id)
    flagged = user_df[user_df["is_anomaly"] == True].sort_values("date_clean", ascending=False)  # noqa: E712
    cols = ["transaction_id_clean", "date_clean", "category_clean", "amount_clean",
            "lower_bound", "upper_bound", "category_median", "notes"]
    records = flagged[cols].copy()
    records["date_clean"] = records["date_clean"].dt.strftime("%Y-%m-%d")
    records = records.fillna("")
    return records.to_dict(orient="records")


class ChatRequest(BaseModel):
    user_id: str
    question: str


@app.post("/api/chat")
def chat(req: ChatRequest):
    get_user_df(req.user_id)  # 404s cleanly if the user_id is bogus
    result = answer_question(req.question, req.user_id, DF)

    context_rows = result["retrieval"]["context_rows"].copy()
    if "date_clean" in context_rows.columns:
        context_rows["date_clean"] = pd.to_datetime(context_rows["date_clean"]).dt.strftime("%Y-%m-%d")
    context_rows = context_rows.fillna("")

    return {
        "answer": result["answer"],
        "matched_count": result["retrieval"]["matched_count"],
        "aggregate": result["retrieval"]["aggregate"],
        "context_rows": context_rows.to_dict(orient="records"),
    }
