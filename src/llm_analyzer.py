import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def _fallback_rca() -> str:
    return (
        "1. What Went Wrong: DQ validation rules failed and/or volume anomaly triggered.\n"
        "2. Possible Root Cause: Upstream API/ETL ingestion partial failure or missing source validation.\n"
        "3. Business Impact: Daily revenue dashboards and customer attribution metrics will be understated.\n"
        "4. Suggested Investigation: Check upstream ingestion logs and inspect rows with NULL customer_id, duplicate transaction_ids, or negative amounts."
    )

def generate_llm_rca(profile: dict, validation: dict, anomaly: dict) -> str | None:
    if validation["passed"] and not anomaly["is_anomaly"]:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        return _fallback_rca()

    prompt = f"""
    You are a Senior Data Reliability Engineer. Analyze this failed data batch and generate a concise root-cause report.

    Batch Profile: {json.dumps(profile)}
    Failed Data Quality Rules: {json.dumps(validation['failed_rules'])}
    Anomaly Detection Results: {json.dumps(anomaly)}

    Provide exact answers under these 4 headings:
1. What Went Wrong
2. Possible Root Cause
3. Business Impact
4. Suggested Investigation (include 1-2 specific SQL checks)
    """

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Warning] OpenAI API unavailable ({type(e).__name__}), using fallback RCA.")
        return _fallback_rca()