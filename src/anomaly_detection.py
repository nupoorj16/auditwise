"""
Step: flag anomalous transactions using per-category IQR bounds.

IQR (not z-score) because amounts are right-skewed, not normally
distributed, and z-score's mean/std are themselves distorted by the
extreme values we're trying to catch. Computed per-category since a
$5,000 Food transaction and a $5,000 Rent transaction are not equally
unusual.
"""
import pandas as pd

def compute_bounds(group: pd.Series) -> pd.Series:
    q1 = group.quantile(0.25)
    q3 = group.quantile(0.75)
    iqr = q3 - q1
    return pd.Series({
        "category_median": group.median(),
        "category_q1": q1,
        "category_q3": q3,
        "lower_bound": max(0.0, q1 - 1.5 * iqr),  # amounts are never negative
        "upper_bound": q3 + 1.5 * iqr,
    })

def add_anomaly_flags(df: pd.DataFrame, amount_col="amount_clean", category_col="category_clean") -> pd.DataFrame:
    df = df.copy()
    bounds = df.groupby(category_col)[amount_col].apply(compute_bounds).unstack()
    df = df.merge(bounds, left_on=category_col, right_index=True, how="left")
    df["is_anomaly"] = (df[amount_col] < df["lower_bound"]) | (df[amount_col] > df["upper_bound"])
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/combined_deduped.csv")
    df = add_anomaly_flags(df)

    print("Total rows:", len(df))
    print("Rows with usable category + amount:", df["is_anomaly"].notna().sum())
    print("Anomalies flagged:", df["is_anomaly"].sum())
    print()
    print("Anomaly rate by category:")
    print(df.groupby("category_clean")["is_anomaly"].mean().sort_values(ascending=False))
    print()
    print("Example: high-value Food anomaly vs similarly-priced non-anomalous Rent")
    food_anomaly = df[(df["category_clean"] == "Food") & (df["is_anomaly"])].nlargest(1, "amount_clean")
    print(food_anomaly[["amount_clean", "category_clean", "lower_bound", "upper_bound", "category_median"]].to_string())

    df.to_csv("data/processed/combined_anomalies.csv", index=False)
    print("Saved to data/processed/combined_anomalies.csv")
