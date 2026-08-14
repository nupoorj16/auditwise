"""
Step: normalize typo/casing variants of `payment_mode` into a fixed canonical set.
"""
import difflib
import pandas as pd

CANONICAL_MODES = ["UPI", "Bank Transfer", "Cash", "Card"]
CANONICAL_LOWER = [c.lower() for c in CANONICAL_MODES]

MANUAL_OVERRIDES = {}

def match_mode(raw_value, cutoff=0.6):
    s = str(raw_value).strip().lower()
    if s in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[s]
    matches = difflib.get_close_matches(s, CANONICAL_LOWER, n=1, cutoff=cutoff)
    if not matches:
        return None
    return CANONICAL_MODES[CANONICAL_LOWER.index(matches[0])]

def build_mode_map(raw_modes, cutoff=0.6) -> dict:
    unique_vals = pd.Series(raw_modes).dropna().unique()
    return {val: match_mode(val, cutoff) for val in unique_vals}

def add_clean_payment_mode(df: pd.DataFrame, cutoff=0.6) -> pd.DataFrame:
    df = df.copy()
    mapping = build_mode_map(df["payment_mode"], cutoff)
    df["payment_mode_clean"] = df["payment_mode"].map(mapping)
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_categories_clean.csv")
    df = add_clean_payment_mode(df)

    unmatched_raw = df.loc[df["payment_mode_clean"].isna(), "payment_mode"].dropna().unique()

    print("Total rows:", len(df))
    print("Unmatched rows:", df["payment_mode_clean"].isna().sum())
    print("Unique raw values unmatched:", sorted(unmatched_raw))
    print()
    print(df["payment_mode_clean"].value_counts())

    df.to_csv("data/processed/combined_payment_mode_clean.csv", index=False)
    print("Saved to data/processed/combined_payment_mode_clean.csv")
