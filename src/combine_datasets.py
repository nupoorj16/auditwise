"""
Step: combine the two raw BudgetWise CSVs into one dataset.

Both files share the same 9 columns but come from unrelated synthetic
sources, so their user_id/transaction_id values coincidentally overlap
(e.g. both have a "U039"). We namespace IDs with A_/B_ prefixes so a
combined transaction_id and user_id are always globally unique, and add
a source_file column to preserve provenance.
"""
import pandas as pd

RAW_A = "data/raw/budgetwise_finance_dataset.csv"
RAW_B = "data/raw/budgetwise_synthetic_dirty.csv"
OUT = "data/processed/combined.csv"


def load_and_namespace(path: str, prefix: str, source_name: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["transaction_id"] = prefix + "_" + df["transaction_id"].astype(str)
    df["user_id"] = prefix + "_" + df["user_id"].astype(str)
    df["source_file"] = source_name
    return df


def combine() -> pd.DataFrame:
    a = load_and_namespace(RAW_A, "A", "budgetwise_finance_dataset.csv")
    b = load_and_namespace(RAW_B, "B", "budgetwise_synthetic_dirty.csv")
    return pd.concat([a, b], ignore_index=True)


if __name__ == "__main__":
    combined = combine()

    print("A rows:", sum(combined["source_file"] == "budgetwise_finance_dataset.csv"))
    print("B rows:", sum(combined["source_file"] == "budgetwise_synthetic_dirty.csv"))
    print("Total rows:", len(combined))
    print("Unique transaction_id:", combined["transaction_id"].nunique())
    print("Columns:", list(combined.columns))

    combined.to_csv(OUT, index=False)
    print(f"Saved to {OUT}")
