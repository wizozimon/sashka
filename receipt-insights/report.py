"""Summarize a local transaction CSV without uploading it anywhere."""
import argparse
import pandas as pd

REQUIRED = {"date", "description", "amount", "category"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()
    df = pd.read_csv(args.csv_path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise SystemExit(f"Missing columns: {', '.join(sorted(missing))}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    invalid = df["date"].isna() | df["amount"].isna()
    if invalid.any():
        print(f"Ignoring {int(invalid.sum())} rows with invalid date/amount")
        df = df.loc[~invalid].copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    expenses = df[df["amount"] < 0].copy()
    expenses["spend"] = -expenses["amount"]
    if expenses.empty:
        print("No expenses found."); return
    print("Monthly spend by category:")
    print(expenses.pivot_table(index="month", columns="category", values="spend", aggfunc="sum", fill_value=0).round(2).to_string())
    print("\nLargest expense transactions:")
    print(expenses.nlargest(args.top, "spend")[ ["date", "description", "category", "spend"] ].to_string(index=False))
    print("\nRecurring merchants/categories (2+ months):")
    recurring = expenses.groupby("description").agg(months=("month", "nunique"), avg_spend=("spend", "mean"))
    print(recurring[recurring["months"] >= 2].sort_values("avg_spend", ascending=False).round(2).to_string())


if __name__ == "__main__":
    main()
