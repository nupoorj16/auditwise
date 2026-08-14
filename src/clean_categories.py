"""
Step: normalize typo/casing variants of `category` into a fixed canonical set.
"""
import difflib
import pandas as pd

CANONICAL_CATEGORIES = [
    "Food", "Rent", "Travel", "Utilities", "Entertainment",
    "Bonus", "Salary", "Others", "Other Income", "Savings",
    "Education", "Health", "Freelance", "Investment",
]
CANONICAL_LOWER = [c.lower() for c in CANONICAL_CATEGORIES]

# Known abbreviations that are semantically clear but too short/dissimilar
# for edit-distance matching to catch on its own.
MANUAL_OVERRIDES = {
    "edu": "Education",
    "misc": "Others",
}

def match_category(raw_value, cutoff=0.6):
    """Fuzzy-match one raw category string to a canonical category, or None if no confident match."""
    s = str(raw_value).strip().lower()
    if s in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[s]
    matches = difflib.get_close_matches(s, CANONICAL_LOWER, n=1, cutoff=cutoff)
    if not matches:
        return None
    return CANONICAL_CATEGORIES[CANONICAL_LOWER.index(matches[0])]

def build_category_map(raw_categories, cutoff=0.6) -> dict:
    unique_vals = pd.Series(raw_categories).dropna().unique()
    return {val: match_category(val, cutoff) for val in unique_vals}

def add_clean_category(df: pd.DataFrame, cutoff=0.6) -> pd.DataFrame:
    df = df.copy()
    mapping = build_category_map(df["category"], cutoff)
    df["category_clean"] = df["category"].map(mapping)
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_dates_clean.csv")
    df = add_clean_category(df)

    print("Total rows:", len(df))
    print("Unmatched (no confident fuzzy match):", df["category_clean"].isna().sum())
    print()
    print("Cleaned category counts:")
    print(df["category_clean"].value_counts())
    print()
    unmatched_raw = df.loc[df["category_clean"].isna(), "category"].dropna().unique()
    print("Unique raw values that went unmatched:", len(unmatched_raw))
    print(sorted(unmatched_raw))

    df.to_csv("data/processed/combined_categories_clean.csv", index=False)
    print("Saved to data/processed/combined_categories_clean.csv")
