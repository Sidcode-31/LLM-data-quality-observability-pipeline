CREATE TABLE IF NOT EXISTS dq_run_history (
    run_id VARCHAR(100) PRIMARY KEY,
    run_date DATE NOT NULL,
    source_file VARCHAR(255),
    row_count INT,
    total_revenue NUMERIC(14, 2),
    null_pct NUMERIC(5, 2),
    duplicate_count INT,
    dq_score NUMERIC(5, 2),
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_reason TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dq_incident_reports (
    incident_id SERIAL PRIMARY KEY,
    run_id VARCHAR(100) REFERENCES dq_run_history(run_id),
    failed_rules JSONB,
    anomaly_details JSONB,
    llm_root_cause TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
