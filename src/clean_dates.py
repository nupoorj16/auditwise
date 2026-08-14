"""
Step: parse the messy `date` column into a real datetime64 column.

Each raw format bucket (see explore_dates.py) gets parsed with its own
exact strptime format string, so there's no ambiguity left for pandas
to guess at.
"""
import pandas as pd
from src.explore_dates import classify_date_format

FORMAT_MAP = {
    "iso": "%Y-%m-%d",              # 2022-04-30
    "slash": "%m/%d/%Y",            # 01/27/2019
    "dash": "%d-%m-%y",             # 26-06-20
    "dash_long_year": "%d-%m-%Y",   # 21-09-2024
    "slash_short_year": "%d/%m/%y", # 29/10/19
    "slash_iso": "%Y/%m/%d",        # 2020/11/17
    "text_month": "%B %d %Y",       # April 05 2019
}

def add_clean_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date_format"] = df["date"].apply(classify_date_format)
    df["date_clean"] = pd.NaT

    for fmt_name, fmt_string in FORMAT_MAP.items():
        mask = df["date_format"] == fmt_name
        df.loc[mask, "date_clean"] = pd.to_datetime(
            df.loc[mask, "date"], format=fmt_string, errors="coerce"
        )
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_amount_clean.csv")
    df = add_clean_date(df)

    originally_null = (df["date_format"] == "null").sum()
    total_null_after = df["date_clean"].isna().sum()
    parse_failures = total_null_after - originally_null

    print("Total rows:", len(df))
    print("Originally null/missing dates:", originally_null)
    print("Null dates after parsing:", total_null_after)
    print("New parse failures (matched a format but still failed):", parse_failures)
    print("Date range:", df["date_clean"].min(), "to", df["date_clean"].max())

    df.to_csv("data/processed/combined_dates_clean.csv", index=False)
    print("Saved to data/processed/combined_dates_clean.csv")
