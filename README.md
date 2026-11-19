\# LLM-Powered Data Reliability \& Observability Framework



An end-to-end automated data quality, ML anomaly detection, and AI root-cause analysis (RCA) observability framework built with \*\*Python, Great Expectations, Scikit-Learn, OpenAI, Apache Airflow, PostgreSQL, Slack, and Grafana\*\*.



\---



\## Architecture Overview



```text

+-------------------+      +------------------------+      +-------------------------+

|  Raw Batch Files  | ---> |  Profiler \& Validator  | ---> |  ML Anomaly Detection   |

|  (CSV / Parquet)  |      |  (Great Expectations)  |      | (Z-Score + Isolation    |

+-------------------+      +------------------------+      |         Forest)         |

&#x20;                                     |                    +-------------------------+

&#x20;                                     v                                 |

&#x20;                          +------------------------+                   |

&#x20;                          |   LLM Root-Cause RCA   | <-----------------+

&#x20;                          | (OpenAI + Fallback RCA)|

&#x20;                          +------------------------+

&#x20;                                |            |

&#x20;                +---------------+            +---------------+

&#x20;                v                                            v

&#x20;   +-------------------------+                  +-------------------------+

&#x20;   |   PostgreSQL Audit DB   |                  |    Slack Webhook Alert  |

&#x20;   |  (Run Metrics + JSONB)  |                  |  (Formatted Incident)   |

&#x20;   +-------------------------+                  +-------------------------+

&#x20;                |

&#x20;                v

&#x20;   +-------------------------+

&#x20;   |    Grafana Dashboard    |

&#x20;   | (DQ Trends \& RCA Logs)  |

&#x20;   +-------------------------+

llm-dq-framework/

├── dags/

│   └── dq\_monitoring\_dag.py     # Apache Airflow TaskFlow orchestration DAG

├── data/

│   └── raw/                     # Synthetic historical \& broken batch datasets

├── sql/

│   └── init.sql                 # PostgreSQL schema (dq\_run\_history \& dq\_incident\_reports)

├── src/

│   ├── anomaly.py               # Z-score \& IsolationForest multivariate anomaly detection

│   ├── db\_logger.py             # PostgreSQL persistence \& historical baseline queries

│   ├── llm\_analyzer.py          # OpenAI root-cause analysis with graceful fallback

│   ├── notifier.py              # Console \& Slack webhook incident alerting

│   ├── profiler.py              # Automated dataset metric \& distribution profiling

│   └── validator.py             # Great Expectations validation suite \& DQ scoring

├── docker-compose.yml           # Multi-container stack (PostgreSQL, Airflow, Grafana)

├── generate\_data.py             # Synthetic 30-day clean + Day 31 broken data generator

├── run\_pipeline.py              # Standalone batch execution runner

├── requirements.txt             # Python dependencies

└── .env.example                 # Environment variable template

