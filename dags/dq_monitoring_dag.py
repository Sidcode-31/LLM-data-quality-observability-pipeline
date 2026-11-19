from datetime import datetime
from airflow.decorators import dag, task
import pandas as pd
from src.profiler import profile_dataframe
from src.validator import validate_dataframe
from src.anomaly import detect_anomalies
from src.llm_analyzer import generate_llm_rca
from src.db_logger import fetch_historical_runs, log_pipeline_run
from src.notifier import send_alert

@dag(
    dag_id="llm_data_quality_pipeline",
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
    tags=["data-quality", "observability", "llm"]
)
def dq_pipeline():

    @task
    def ingest_and_profile(filepath: str):
        df = pd.read_csv(filepath)
        return {"filepath": filepath, "profile": profile_dataframe(df)}

    @task
    def run_validation(payload: dict):
        df = pd.read_csv(payload["filepath"])
        return validate_dataframe(df)

    @task
    def run_anomaly_check(payload: dict):
        history_df = fetch_historical_runs(limit=30)
        return detect_anomalies(payload["profile"], history_df)

    @task
    def analyze_and_alert(payload: dict, validation: dict, anomaly: dict):
        filepath = payload["filepath"]
        profile = payload["profile"]
        llm_rca = generate_llm_rca(profile, validation, anomaly)
        run_id = f"airflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_date = datetime.now().strftime("%Y-%m-%d")

        log_pipeline_run(run_id, run_date, filepath, profile, validation, anomaly, llm_rca)
        send_alert(run_id, filepath, validation["dq_score"], anomaly, llm_rca)

    data_payload = ingest_and_profile("/opt/airflow/data/raw/orders_2026_12_01_broken.csv")
    val_res = run_validation(data_payload)
    anom_res = run_anomaly_check(data_payload)
    analyze_and_alert(data_payload, val_res, anom_res)

dq_pipeline()