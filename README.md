# Bluestock Fintech — Mutual Fund Analytics Platform

An industry-grade, end-to-end data engineering and analytics platform built for the **Bluestock Fintech Capstone Project**.

---

## Project Objectives & Architecture

This platform implements an **Extract → Transform → Load → Analyze → Visualize** pipeline that consolidates fragmented mutual fund data, loads it into a normalized SQLite star-schema database, calculates risk-adjusted return metrics, and provides an interactive analytical dashboard.

```
Extract (APIs + CSVs) → Transform (Pandas) → Load (SQLite) → Analyze (EDA & Risk) → Visualize (Power BI / Tableau)
```

### Star Schema Tables
`dim_fund` · `dim_date` · `fact_nav` · `fact_aum` · `fact_sip` · `fact_transactions`

### Source Datasets (10 CSV files)
`01_fund_master` · `02_nav_history` · `03_aum_by_fund_house` · `04_monthly_sip_inflows` · `05_category_inflows` · `06_industry_folio_count` · `07_scheme_performance` · `08_investor_transactions` · `09_portfolio_holdings` · `10_benchmark_indices`

---

## Milestone & Execution Roadmap (7 Days)

| Day   | Milestone                                  |
|-------|---------------------------------------------|
| 1–2   | ETL Pipeline + SQLite Database              |
| 3     | Star Schema + EDA Notebook (15+ charts)     |
| 4     | Risk & Performance Metrics                  |
| 5     | Dashboard Build (Power BI / Tableau)        |
| 6     | Demographics & Benchmark Analysis           |
| 7     | Final PDF Report + GitHub Portfolio Polish   |

---

## Day 1: Project Setup & Data Ingestion

The objective of Day 1 is to:
1. Establish the repository structure with all required directories.
2. Ingest all 10 historical CSV datasets, logging shapes, null counts, duplicate counts, and dtypes.
3. Explore fund master — print unique fund houses, categories, sub-categories, and risk grades.
4. Fetch live NAV data for targeted mutual fund schemes from `api.mfapi.in`.
5. Run cross-dataset AMFI code validation between fund master and NAV history.
6. Generate automated ingestion summary and data quality audit reports.

---

## Directory Layout

```
Internship_coding/
├── .gitignore
├── README.md
├── requirements.txt
├── data_sets/               # Original 10 source CSVs (read-only)
├── data/
│   ├── raw/                 # Ingested copies + live NAV files
│   └── processed/           # Cleaned/normalized output (Day 2+)
├── notebooks/               # Jupyter Notebooks for EDA (Day 3)
├── reports/                 # Ingestion summaries, audit reports, logs
│   ├── etl_pipeline.log
│   ├── data_ingestion_summary.txt
│   └── data_quality_report.md
├── sql/                     # SQLite schema DDL & queries (Day 2)
├── dashboard/               # Power BI / Tableau files (Day 5)
├── src/                     # Modular Python ETL scripts
│   ├── __init__.py
│   ├── config.py            # Central path settings & API targets
│   ├── data_ingestion.py    # Day 1: Dataset loading & exploration
│   ├── live_nav_fetch.py    # Day 1: mfapi.in REST API NAV downloader
│   └── data_quality_report.py  # Day 1: AMFI code integrity validator
└── project_description/     # Capstone task cards & architecture diagrams
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git

### 1. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Data Ingestion (Step 1)
Copies all 10 CSVs into `data/raw/`, prints shape, dtypes, head, null counts, duplicates, and explores fund master:
```bash
python src/data_ingestion.py
```
**Outputs:**
### 4. Run Live NAV Download (Tasks 4 & 5)
Fetches latest NAV data from `api.mfapi.in`. This script auto-invokes the HDFC Top 100 demo (Task 4) first, followed by the 5 key target schemes (Task 5):
```bash
python src/live_nav_fetch.py
```
**Outputs:**
- `data/raw/raw_nav_{amfi_code}.csv` — Total 6 CSVs

### 5. Explore Fund Master via Notebook (Task 6)
Open the Jupyter notebook to see the fund houses, categories, sub-categories, and risk grades:
```bash
jupyter notebook notebooks/fund_master_exploration.ipynb
```

*(Note: Data Quality Audit (Task 7) is executed automatically at the end of `data_ingestion.py` and produces `reports/data_quality_report.md`)*

---

## Tech Stack
- **Python** · Pandas · NumPy · Matplotlib · Seaborn · Plotly
- **SQLAlchemy** · SQLite / PostgreSQL
- **Requests** · scipy
- **Power BI / Tableau** (Dashboard)
- **Git / GitHub** (Version Control)

---

## Author
Capstone Intern — Bluestock Fintech
