import os
import json
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_pg_conn():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DB", "dq_observability"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "postgres")
    )

def fetch_historical_runs(limit: int = 30) -> pd.DataFrame:
    conn = get_pg_conn()
    query = f"""
        SELECT run_date, row_count, total_revenue, null_pct, dq_score
        FROM dq_run_history
        WHERE status = 'PASSED'
        ORDER BY run_date DESC
        LIMIT {limit};
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def log_pipeline_run(run_id: str, run_date: str, source_file: str, profile: dict, validation: dict, anomaly: dict, llm_rca: str | None):
    conn = get_pg_conn()
    cur = conn.cursor()
    status = "FAILED" if (not validation["passed"] or anomaly["is_anomaly"]) else "PASSED"

    cur.execute("""
        INSERT INTO dq_run_history (
            run_id, run_date, source_file, row_count, total_revenue,
            null_pct, duplicate_count, dq_score, is_anomaly, anomaly_reason, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (run_id) DO UPDATE SET
            dq_score = EXCLUDED.dq_score,
            is_anomaly = EXCLUDED.is_anomaly,
            status = EXCLUDED.status;
    """, (
        run_id, run_date, source_file, profile["row_count"], profile["total_revenue"],
        profile["null_pct"], profile["duplicate_txns"], validation["dq_score"],
        anomaly["is_anomaly"], "; ".join(anomaly["reasons"]), status
    ))

    if status == "FAILED":
        cur.execute("""
            INSERT INTO dq_incident_reports (run_id, failed_rules, anomaly_details, llm_root_cause)
            VALUES (%s, %s, %s, %s);
        """, (
            run_id, json.dumps(validation["failed_rules"]), json.dumps(anomaly), llm_rca
        ))

    conn.commit()
    cur.close()
    conn.close()