import requests
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Define the issues to be created
issues = [
    {
        "title": "Cache configuration files instead of reloading per execution",
        "body": "Currently, YAML files in `config/` are loaded every time `ConfigManager` is called. Optimize by loading once and caching during ETL runtime.\n\n**Acceptance Criteria:**\n- Configs load once and are reused throughout the pipeline.\n- Pipeline behavior remains identical.\n- No more redundant I/O to `config/` during runtime.",
        "labels": ["enhancement", "performance"]
    },
    {
        "title": "Expand `_validate_data_columns()` to check types and ranges",
        "body": "The current method checks for missing columns. Extend it to:\n- Verify data types (e.g., float, int, str)\n- Optionally validate ranges or categorical values\n\n**Acceptance Criteria:**\n- Clear error if column contains unexpected type or out-of-bound values\n- Validation logic configurable in `config/schema.yaml`",
        "labels": ["enhancement", "validation"]
    },
    {
        "title": "Preprocess Excel input to Parquet/CSV for performance",
        "body": "Move Excel normalization out of runtime. Use a pre-ETL step to convert to `data/processed/`, skip conversion if file is up-to-date.\n\n**Acceptance Criteria:**\n- Supports both `.csv` and `.parquet` as output\n- Automatically skips conversion if file is unchanged\n- Downstream pipeline uses these processed files",
        "labels": ["performance", "data"]
    },
    {
        "title": "Orchestrate pipeline with Airflow or Prefect",
        "body": "Modularize the ETL flow (data load → business logic → formatting) and implement as a DAG (or flow) for scheduled execution.\n\n**Acceptance Criteria:**\n- Pipeline runnable via Airflow (DAG with 3+ tasks) or Prefect\n- Logs each stage, fails gracefully on errors\n- Can run daily/weekly",
        "labels": ["orchestration", "automation"]
    },
    {
        "title": "Implement structured logging across pipeline",
        "body": "Use Python’s `logging` module to replace all `print()` and `sys.exit()` calls. Include timestamp, log level, and module.\n\n**Acceptance Criteria:**\n- All pipeline components write to a centralized log\n- Includes log rotation and warning/error capture\n- Logs saved to `logs/` or pushed to stdout",
        "labels": ["logging", "refactor"]
    },
    {
        "title": "Allow partial credit in progress score calculations",
        "body": "Currently, `BusinessLogicCalculator` uses binary 0/100 scores. Refactor to assign proportional credit based on actual progress vs. thresholds.\n\n**Acceptance Criteria:**\n- Scores scale with progress %\n- Configurable via `okr_criteria.yaml`\n- Optionally include color-coded status (e.g., green/yellow/red)",
        "labels": ["KPI", "refactor"]
    },
    {
        "title": "Calculate delta between periods in OKR progress",
        "body": "Track acceleration or stagnation by storing and comparing progress over time.\n\n**Acceptance Criteria:**\n- Stores last period’s scores\n- Adds rate-of-change column\n- Optionally plots trends (CLI, Matplotlib, or export)",
        "labels": ["KPI", "trend"]
    },
    {
        "title": "Save timestamped OKR results for trend analysis",
        "body": "Persist results to a file-based or DB store (e.g., SQLite or flat CSVs in `data/results/`) for reporting and reanalysis.\n\n**Acceptance Criteria:**\n- Each KPI run saves output with a timestamp\n- Supports reload for dashboard or comparison\n- Optional export to JSON or CSV",
        "labels": ["data", "KPI"]
    },
    {
        "title": "Allow editing OKR weights and thresholds without code changes",
        "body": "Expose KPI weights and pass/fail thresholds via environment variables or lightweight front-end interface.\n\n**Acceptance Criteria:**\n- Can override defaults using `.env` or CLI params\n- Validates that weights sum to 100%\n- Warns if thresholds are inconsistent",
        "labels": ["KPI", "config"]
    },
    {
        "title": "Extend presentation formatter to export multiple formats",
        "body": "Currently `format_okr_tracker()` outputs Markdown. Add export to JSON, CSV, and optional REST API (Flask or FastAPI).\n\n**Acceptance Criteria:**\n- Exports saved to `/reports/` in multiple formats\n- REST API (optional) provides latest KPIs at `/okr`\n- All exports contain the same KPI content",
        "labels": ["export", "API"]
    }
]

# GitHub API endpoint
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Create each issue
for issue in issues:
    response = requests.post(api_url, headers=headers, json=issue)
    if response.status_code == 201:
        print(f"Issue created: {issue['title']}")
    else:
        print(f"Failed to create issue: {issue['title']}")
        print(f"Response: {response.status_code} - {response.text}")
