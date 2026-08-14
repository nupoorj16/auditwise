"""
Step: clean the `amount` column.
Raw values look like: '998', '$143', '83,802', '₹5070', 'Rs.828', '999999999'
"""
import pandas as pd
import re

SENTINEL = 999999999

def clean_amount(val):
    """Turn a messy amount string into a float, or None if unparseable."""
    if pd.isna(val):
        return None
    s = str(val)
    s = re.sub(r"[₹$,]|Rs\.?", "", s)
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        return None

def add_clean_amount(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amount_clean"] = df["amount"].apply(clean_amount)
    df["was_sentinel"] = df["amount_clean"] == SENTINEL
    df.loc[df["was_sentinel"], "amount_clean"] = None
    p99 = df["amount_clean"].quantile(0.99)
    df["is_outlier"] = df["amount_clean"] > p99
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined.csv")
    df = add_clean_amount(df)

    print("Total rows:", len(df))
    print("Sentinel values converted to null:", df["was_sentinel"].sum())
    print("Total missing/unparseable amounts:", df["amount_clean"].isna().sum())
    print("Outliers flagged:", df["is_outlier"].sum())

    df.to_csv("data/processed/combined_amount_clean.csv", index=False)
    print("Saved to data/processed/combined_amount_clean.csv")
