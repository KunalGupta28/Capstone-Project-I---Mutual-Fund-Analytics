# Bluestock Fintech Mutual Fund Analytics Platform

An industry-grade, end-to-end data engineering and analytics platform built for the **Bluestock Fintech Mutual Fund Analytics Platform Capstone Project**.

---

## Project Objectives & Architecture
This platform implements an **Extract-Transform-Load (ETL)** pipeline that consolidates fragmented mutual fund data, loads it into a normalized SQLite database star schema, calculates risk-adjusted return metrics, and provides an interactive analytical dashboard.

```
Extract (APIs, CSVs) ──> Transform (Pandas) ──> Load (SQLite) ──> Analyze (EDA & Risk) ──> Visualize (Power BI)
```

---

## Day 1: Project Setup & Data Ingestion

The objective of Day 1 is to:
1. Establish the repository structure.
2. Ingest 10 historical datasets, logging stats (shapes, null counts, duplicate counts, schema types).
3. Fetch live NAV statistics for targeted mutual fund schemes from `api.mfapi.in`.
4. Run cross-dataset validation checks (AMFI code audits between the master catalog and history files).
5. Compile and generate automated ingestion and audit reports.

---

## Directory Layout

```
bluestock-mf-analytics/
├── .gitignore               # Standard Git ignore profiles
├── README.md                # Project documentation
├── requirements.txt         # Package dependencies
├── Invoke-ExternalCommand.ps1 # Thread-safe execution wrapper for sandboxed terminals
├── config/                  # External configurations
├── data/
│   ├── raw/                 # Ingested raw source CSVs & live NAV files
│   └── processed/           # Day 2 database imports (normalized output)
├── notebooks/               # Jupyter Notebooks for EDA (Day 3)
├── reports/                 # Output audit reports, log sheets, and summary sheets
│   ├── etl_pipeline.log     # Detailed execution logging
│   ├── data_ingestion_summary.txt # Ingestion stats summary
│   └── data_quality_report.md     # Referential integrity check logs
├── sql/                     # SQLite schema definitions & SQL queries (Day 2)
├── src/                     # Modular Python sources
│   ├── __init__.py
│   ├── config.py            # Central folder settings & targets config
│   ├── data_ingestion.py    # Raw CSV ingestion and summary auditor
│   ├── live_nav_fetch.py    # mfapi.in REST API live NAV downloader
│   └── data_quality_report.py # AMFI key integrity validator
└── tests/                   # Ingestion unit tests
```

---

## Technical Note: Hosted Runspace Workaround
During development inside sandboxed environments (such as some AI-powered terminal runners), standard process execution commands in PowerShell can fail with a `DriveNotFoundException` pointing to a missing `Microsoft.PowerShell.Core\FileSystem` drive mapping.

To bypass this platform bug, the utility script `Invoke-ExternalCommand.ps1` was created. It wraps the .NET `System.Diagnostics.Process` API directly to spawn processes outside PowerShell's pipeline context, utilizing thread-safe `ConcurrentQueue` structures to pipe standard output in real-time.

---

## Getting Started

### 1. Set Up Environment
Ensure Python 3.10+ is installed on your local system. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Ingestion Script
Ingests and prints basic statistics of the 10 core CSV datasets, moving them into the structured `data/raw/` path:
```bash
python src/data_ingestion.py
```
*Outputs statistics directly to `reports/data_ingestion_summary.txt` and `reports/etl_pipeline.log`.*

### 3. Run Live NAV Download
Calls the `mfapi.in` API to download the latest NAV logs for selected schemes:
```bash
python src/live_nav_fetch.py
```
*Stores individual raw JSON outputs converted to CSVs under `data/raw/raw_nav_{amfi_code}.csv`.*

### 4. Run Referential Audit
Audits scheme code connections between `fund_master` and `nav_history`:
```bash
python src/data_quality_report.py
```
*Generates the audit validation report directly inside `reports/data_quality_report.md`.*
