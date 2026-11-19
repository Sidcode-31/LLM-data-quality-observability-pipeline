import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_alert(run_id: str, source_file: str, dq_score: float, anomaly: dict, llm_rca: str | None):
    if dq_score == 100.0 and not anomaly["is_anomaly"]:
        return

    message = (
        f"🚨 *Data Quality Incident Detected* (`{run_id}`)\n"
        f"*File:* `{source_file}` | *DQ Score:* `{dq_score}%` | *Anomaly:* `{anomaly['is_anomaly']}`\n\n"
        f"*LLM Root-Cause Analysis:*\n{llm_rca}"
    )
    print("\n" + "="*60 + "\n" + message + "\n" + "="*60 + "\n")

    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if webhook and webhook.startswith("https://"):
        requests.post(webhook, json={"text": message}, timeout=10)