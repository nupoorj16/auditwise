"""
Step: turn each cleaned transaction row into one retrieval chunk.

One transaction = one chunk. Aggregation/filtering questions are
answered by structured filtering over the clean columns (pandas), not
by retrieving chunks and asking the LLM to add numbers up. Chunk text
exists so semantic search can match free-text queries (e.g. mentions
of a merchant or description) against the `notes` field.
"""
import pandas as pd

def build_chunk_text(row) -> str:
    date_str = row["date_clean"][:10] if pd.notna(row["date_clean"]) else "unknown date"
    amount = row["amount_clean"]
    amount_str = f"${amount:,.2f}" if pd.notna(amount) else "unknown amount"
    category = row["category_clean"] if pd.notna(row["category_clean"]) else "Uncategorized"
    mode = row["payment_mode_clean"] if pd.notna(row["payment_mode_clean"]) else "unknown payment method"
    location = row["location"] if pd.notna(row["location"]) else "unknown location"
    notes = row["notes"] if pd.notna(row["notes"]) else ""

    text = f"{date_str}: {row['transaction_type']} of {amount_str} in category {category}, paid via {mode} in {location}."
    if notes:
        text += f" Note: {notes}."
    if row.get("is_anomaly"):
        text += " This transaction was flagged as statistically unusual for its category."
    return text

def build_chunks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["chunk_text"] = df.apply(build_chunk_text, axis=1)
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_anomalies.csv")
    df = build_chunks(df)

    print("Total chunks:", len(df))
    print()
    print("Sample chunks:")
    for text in df["chunk_text"].sample(5, random_state=1):
        print("-", text)

    df.to_csv("data/processed/combined_chunked.csv", index=False)
    print("\nSaved to data/processed/combined_chunked.csv")
