"""
Step: embed each transaction chunk and store it in a local Chroma vector DB.

Chroma's OpenAIEmbeddingFunction embeds automatically on add() and on
query(), so retrieval code never has to call the embeddings API by hand.
Metadata is stored alongside each vector so retrieval can combine
structured filtering (Chroma `where` clauses) with semantic search in
one call - that's the "hybrid" part of hybrid retrieval.
"""
import os

# Must run before importing chromadb: many hosts (Render included) ship a
# system sqlite3 older than what Chroma requires, which crashes at import
# time. Swap in the modern pysqlite3-binary build first, when available.
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "transactions"
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 500


def build_metadata(row) -> dict:
    return {
        "transaction_id": str(row["transaction_id_clean"]),
        "user_id": str(row["user_id"]),
        "date": str(row["date_clean"])[:10] if pd.notna(row["date_clean"]) else "",
        "category": str(row["category_clean"]) if pd.notna(row["category_clean"]) else "Uncategorized",
        "amount": float(row["amount_clean"]) if pd.notna(row["amount_clean"]) else -1.0,
        "payment_mode": str(row["payment_mode_clean"]) if pd.notna(row["payment_mode_clean"]) else "unknown",
        "location": str(row["location"]) if pd.notna(row["location"]) else "unknown",
        "transaction_type": str(row["transaction_type"]) if pd.notna(row["transaction_type"]) else "unknown",
        "is_anomaly": bool(row["is_anomaly"]) if pd.notna(row["is_anomaly"]) else False,
    }


def get_collection():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and fill in your key.")

    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key, model_name=EMBEDDING_MODEL
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)


def load_into_chroma(df: pd.DataFrame):
    """Rebuilds the collection from scratch so it never drifts out of sync
    with the source CSV if cleaning/anomaly logic changes upstream."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and fill in your key.")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(name=COLLECTION_NAME)

    collection = get_collection()

    for start in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[start:start + BATCH_SIZE]
        collection.add(
            ids=batch["transaction_id_clean"].astype(str).tolist(),
            documents=batch["chunk_text"].tolist(),
            metadatas=[build_metadata(row) for _, row in batch.iterrows()],
        )
        print(f"Embedded rows {start} to {start + len(batch)}")

    return collection


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_chunked.csv")

    print(f"Loading {len(df)} chunks into Chroma (this calls the OpenAI embeddings API)...")
    collection = load_into_chroma(df)

    print("Collection count:", collection.count())
    result = collection.query(query_texts=["restaurant dinner"], n_results=3)
    print("\nSanity-check query 'restaurant dinner':")
    for doc in result["documents"][0]:
        print("-", doc)
