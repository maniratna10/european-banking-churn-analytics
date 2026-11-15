
"""Reproducible data checks and segmentation for the European banking churn project."""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "european_bank.csv")

required = ["CustomerId","CreditScore","Geography","Gender","Age","Tenure","Balance",
            "NumOfProducts","HasCrCard","IsActiveMember","EstimatedSalary","Exited"]
missing_columns = sorted(set(required) - set(df.columns))
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

print("Rows, columns:", df.shape)
print("Missing values by column:\n", df.isna().sum())
print("Duplicate rows:", int(df.duplicated().sum()))
print("Duplicate customer IDs:", int(df["CustomerId"].duplicated().sum()))
for col in ["Exited","HasCrCard","IsActiveMember"]:
    print(f"{col} values:", sorted(df[col].dropna().unique().tolist()))
    if not set(df[col].dropna().unique()).issubset({0,1}):
        raise ValueError(f"{col} should contain only 0/1 values")

positive = df.loc[df.Balance > 0, "Balance"]
df["AgeGroup"] = pd.cut(df.Age, [0,29,45,59,120],
    labels=["Under 30","30–45","46–59","60+"], include_lowest=True)
df["TenureGroup"] = pd.cut(df.Tenure, [-1,3,7,10],
    labels=["New (0–3 years)","Mid-term (4–7 years)","Long-term (8–10 years)"])
df["CreditBand"] = pd.qcut(df.CreditScore, 3, labels=["Low","Medium","High"])
midpoint = positive.median()
df["BalanceSegment"] = np.select([df.Balance.eq(0),df.Balance.lt(midpoint)],
    ["Zero balance","Low balance"],default="High balance")
premium = positive.quantile(.75)
df["HighValueBalance"] = df.Balance >= premium

print("Overall churn rate:", round(df.Exited.mean(),4))
for segment in ["Geography","AgeGroup","CreditBand","TenureGroup","BalanceSegment","Gender","NumOfProducts","IsActiveMember"]:
    print("\\n", segment)
    print(df.groupby(segment, observed=True).Exited.agg(["count","sum","mean"]).to_string())
print("\\nPositive-balance median:", round(midpoint,2))
print("High-value balance threshold (positive-balance P75):", round(premium,2))
print("Churned customer balance sum:", round(df.loc[df.Exited.eq(1),"Balance"].sum(),2))
