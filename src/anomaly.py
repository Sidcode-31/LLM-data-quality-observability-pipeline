import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(today_profile: dict, history_df: pd.DataFrame) -> dict:
    if history_df.empty or len(history_df) < 5:
        return {"is_anomaly": False, "reasons": [], "baseline_revenue": None}

    mean_rev = float(history_df["total_revenue"].mean())
    std_rev = float(history_df["total_revenue"].std()) or 1.0
    mean_rows = float(history_df["row_count"].mean())
    std_rows = float(history_df["row_count"].std()) or 1.0

    today_rev = today_profile["total_revenue"]
    today_rows = today_profile["row_count"]

    rev_z = (today_rev - mean_rev) / std_rev
    row_z = (today_rows - mean_rows) / std_rows

    reasons = []
    if abs(rev_z) > 2.5:
        pct_change = round(((today_rev - mean_rev) / mean_rev) * 100, 1)
        reasons.append(f"Revenue anomaly: {today_rev} vs historical avg {round(mean_rev, 2)} ({pct_change}%, Z={round(rev_z, 2)})")

    if abs(row_z) > 2.5:
        reasons.append(f"Row count anomaly: {today_rows} vs historical avg {round(mean_rows, 1)} (Z={round(row_z, 2)})")

    # Multivariate check with IsolationForest when >= 15 historical runs exist
    if len(history_df) >= 15:
        features = ["row_count", "total_revenue", "null_pct"]
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(history_df[features])
        pred = clf.predict([[today_rows, today_rev, today_profile["null_pct"]]])[0]
        if pred == -1 and not reasons:
            reasons.append("IsolationForest flagged multivariate distribution shift across row_count, revenue, and null_pct.")

    return {
        "is_anomaly": len(reasons) > 0,
        "reasons": reasons,
        "baseline_revenue": round(mean_rev, 2),
        "baseline_rows": round(mean_rows, 1)
    }