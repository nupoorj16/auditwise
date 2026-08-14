"""
Step: figure out what date formats we actually have before parsing anything.
"""
import re
import pandas as pd

def classify_date_format(val):
    if pd.isna(val):
        return "null"
    s = str(val).strip()

    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return "iso"          # e.g. 2022-04-30

    if re.match(r"^\d{2}/\d{2}/\d{4}$", s):
        return "slash"        # e.g. 01/27/2019

    if re.match(r"^\d{2}-\d{2}-\d{2}$", s):
        return "dash"         # e.g. 26-06-20

    if re.match(r"^\d{2}-\d{2}-\d{4}$", s):
        return "dash_long_year"  # e.g. 21-09-2024

    if re.match(r"^[A-Za-z]+ \d{2} \d{4}$", s):
        return "text_month"   # e.g. April 05 2019
    
    if re.match(r"^\d{2} [A-Za-z]+ \d{4}$", s):
        return "text_month_alt"  # e.g. 05 April 2019
    
    if re.match(r"^\d{2}/\d{2}/\d{2}$", s):
        return "slash_short_year"  # e.g. 01/27/19
    
    if re.match(r"^\d{4}/\d{2}/\d{2}$", s):
        return "slash_iso"  # e.g. 2020/11/17

    return "unmatched"


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_amount_clean.csv")

    df["date_format"] = df["date"].apply(classify_date_format)

    print("Bucket counts:")
    print(df["date_format"].value_counts())

    print()
    print("Sample of 'unmatched' values (if any):")
    print(df.loc[df["date_format"] == "unmatched", "date"].unique()[:20])
