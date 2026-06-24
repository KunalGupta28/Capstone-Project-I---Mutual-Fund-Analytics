import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
SQL_DIR = BASE_DIR / "sql"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Source Data sets (where original files are initially placed)
SOURCE_DATASETS_DIR = BASE_DIR / "data_sets"

# Target schemes for Live NAV Ingestion
HDFC_NAV_TARGET = {
    "125497": "HDFC_Top_100_Direct"
}

LIVE_NAV_TARGETS = {
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

# API Endpoint Base
MF_API_BASE_URL = "https://api.mfapi.in/mf"

# Ensure all structural directories exist
for folder in [DATA_RAW_DIR, DATA_PROCESSED_DIR, REPORTS_DIR, NOTEBOOKS_DIR, SQL_DIR, DASHBOARD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
