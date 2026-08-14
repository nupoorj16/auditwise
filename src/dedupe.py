"""
Step: remove true duplicate rows, and disambiguate transaction_id collisions
(same id, different underlying transaction) rather than dropping real data.
"""
import pandas as pd

ORIG_COLS = [
    "transaction_id", "user_id", "date", "transaction_type", "category",
    "amount", "payment_mode", "location", "notes", "source_file",
]

def dedupe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates(subset=ORIG_COLS, keep="first").reset_index(drop=True)

    occurrence = df.groupby("transaction_id").cumcount()  # 0 for first row in group, 1/2/... for repeats
    df["transaction_id_clean"] = df["transaction_id"]
    needs_suffix = occurrence > 0
    df.loc[needs_suffix, "transaction_id_clean"] = (
        df.loc[needs_suffix, "transaction_id"] + "_dup" + occurrence[needs_suffix].astype(str)
    )

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_payment_mode_clean.csv")
    n_before = len(df)

    df = dedupe(df)

    print("Rows before:", n_before)
    print("Rows after dropping exact duplicates:", len(df))
    print("Exact duplicates dropped:", n_before - len(df))
    print("ID collisions disambiguated:", (df["transaction_id"] != df["transaction_id_clean"]).sum())
    print("Unique transaction_id_clean:", df["transaction_id_clean"].nunique(), "vs total rows:", len(df))

    df.to_csv("data/processed/combined_deduped.csv", index=False)
    print("Saved to data/processed/combined_deduped.csv")
