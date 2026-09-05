# Financial analytics, trend modeling, and spending prediction engine — Noor
import pandas as pd
from sklearn.ensemble import IsolationForest

def monthly_category_totals(expenses: list[dict]) -> list[dict]:
    if not expenses:
        return []
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    result = df.groupby(["month", "category"])["amount"].sum().reset_index()
    return result.to_dict(orient="records")

def detect_anomalies(expenses: list[dict]) -> list[str]:
    if len(expenses) < 10:
        return []
    df = pd.DataFrame(expenses)
    model = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly"] = model.fit_predict(df[["amount"]])
    return df.loc[df["anomaly"] == -1, "id"].astype(str).tolist()