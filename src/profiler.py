import pandas as pd

EXPECTED_SCHEMA = {
    "transaction_id": "object",
    "customer_id": "object",
    "email": "object",
    "amount": "float64",
    "created_at": "object"
}

def profile_dataframe(df: pd.DataFrame) -> dict:
    missing_cols = [c for c in EXPECTED_SCHEMA if c not in df.columns]
    extra_cols = [c for c in df.columns if c not in EXPECTED_SCHEMA]
    
    return {
        "row_count": int(len(df)),
        "total_revenue": round(float(df["amount"].sum()), 2) if "amount" in df.columns else 0.0,
        "null_pct": round(float(df.isnull().mean().mean() * 100), 2),
        "nulls_by_col": df.isnull().sum().to_dict(),
        "duplicate_txns": int(df["transaction_id"].duplicated().sum()) if "transaction_id" in df.columns else 0,
        "min_amount": round(float(df["amount"].min()), 2) if "amount" in df.columns else 0.0,
        "max_amount": round(float(df["amount"].max()), 2) if "amount" in df.columns else 0.0,
        "mean_amount": round(float(df["amount"].mean()), 2) if "amount" in df.columns else 0.0,
        "schema_drift": {"missing_columns": missing_cols, "extra_columns": extra_cols}
    }