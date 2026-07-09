# Bluestock Fintech — Mutual Fund Analytics Platform

An industry-grade, end-to-end data engineering and analytics platform built for the **Bluestock Fintech Capstone Project**.

---

## Project Objectives & Architecture

This platform implements an **Extract → Transform → Load → Analyze → Visualize** pipeline that consolidates fragmented mutual fund data, loads it into a normalized SQLite star-schema database, calculates risk-adjusted return metrics, and provides an interactive analytical dashboard.

```
Extract (APIs + CSVs) → Transform (Pandas) → Load (SQLite) → Analyze (EDA & Risk) → Visualize (Power BI / Tableau)
```

### Star Schema Tables
`dim_fund` · `dim_date` · `fact_nav` · `fact_aum` · `fact_sip_industry` · `fact_transactions` · `fact_performance` · `fact_portfolio`

### Source Datasets (10 CSV files)
`01_fund_master` · `02_nav_history` · `03_aum_by_fund_house` · `04_monthly_sip_inflows` · `05_category_inflows` · `06_industry_folio_count` · `07_scheme_performance` · `08_investor_transactions` · `09_portfolio_holdings` · `10_benchmark_indices`

---

## Milestone & Execution Roadmap (7 Days)

| Day   | Milestone                                  | Key Deliverables                                              |
|-------|---------------------------------------------|---------------------------------------------------------------|
| 1–2   | ETL Pipeline + SQLite Database              | `data_ingestion.py`, `data_cleaning.py`, `db_loader.py`, `bluestock_mf.db` |
| 3     | Star Schema + EDA Notebook (15+ charts)     | `03_eda_analysis.ipynb`, 15 chart PNGs in `reports/`          |
| 4     | Risk & Performance Metrics                  | `compute_metrics.py`, `fund_scorecard.csv`, CAGR/Sharpe/Sortino CSVs |
| 5     | Dashboard Build (Power BI)                  | `bluestock_mf_dashboard.pbix`, 4-page interactive dashboard    |
| 6     | Advanced Analytics & Demographics           | `05_advanced_analytics.ipynb`, VaR/CVaR, HHI, Cohort, Recommender |
| 7     | Final PDF Report + Presentation + GitHub    | `Final_Report.pdf` (15–20 pages), `Presentation.pptx` (12 slides) |

---

## Directory Layout

```
Internship_coding/
├── .gitignore
├── README.md
├── requirements.txt
├── Bluestock_MF_Capstone_Project.pdf    # Original capstone brief
├── data_sets/                           # Original 10 source CSVs (read-only)
├── data/
│   ├── raw/                             # Ingested copies + live NAV files
│   ├── processed/                       # Cleaned/normalized CSVs
│   │   ├── clean_nav.csv
│   │   ├── clean_transactions.csv
│   │   ├── clean_performance.csv
│   │   ├── fund_scorecard.csv
│   │   ├── cagr_report.csv
│   │   ├── var_cvar_report.csv
│   │   ├── investor_cohort_analysis.csv
│   │   ├── hhi_concentration.csv
│   │   └── data_dictionary.md
│   └── db/
│       └── bluestock_mf.db             # SQLite star-schema database (gitignored)
├── notebooks/
│   ├── 01_data_ingestion.ipynb          # Day 1: Dataset profiling & live NAV fetch
│   ├── 02_data_cleaning.ipynb           # Day 2: Cleaning pipeline & DB verification
│   ├── 03_eda_analysis.ipynb            # Day 3: 15+ EDA visualizations
│   ├── 04_performance_analytics.ipynb   # Day 4: Performance scorecard & risk metrics
│   ├── 05_advanced_analytics.ipynb      # Day 6: VaR, CVaR, HHI, Cohort, Recommender
│   └── fund_master_exploration.ipynb    # Day 1: Fund master unique values exploration
├── reports/
│   ├── Final_Report.pdf                 # 15–20 page business report
│   ├── Presentation.pptx               # 12-slide presentation deck
│   ├── EDA_Findings.md                  # EDA insight summary
│   ├── data_ingestion_summary.txt       # Per-dataset ingestion profiles
│   ├── data_quality_report.md           # AMFI code integrity audit
│   ├── etl_pipeline.log                 # Full pipeline execution log
│   ├── chart_01_nav_trends.png          # ... through chart_15_gender_sip.png
│   ├── rolling_sharpe_chart.png
│   ├── benchmark_chart.png
│   └── advanced_*.png                   # VaR, HHI, Cohort, SIP continuity charts
├── sql/
│   ├── schema.sql                       # DDL for 8 star-schema tables + indexes
│   └── queries.sql                      # 10 analytical SQL queries
├── dashboard/
│   ├── bluestock_mf_dashboard.pbix      # Power BI Desktop file (4 pages)
│   ├── Dashboard.pdf                    # Exported dashboard pages
│   └── page_1.png ... page_4.png        # Dashboard screenshots
├── scripts/                             # All Python ETL & analysis scripts
│   ├── __init__.py
│   ├── config.py                        # Central path settings & API targets
│   ├── data_ingestion.py                # Day 1: Dataset loading & exploration
│   ├── live_nav_fetch.py                # Day 1: mfapi.in REST API NAV downloader
│   ├── hdfc_nav_demo.py                 # Day 1: HDFC Top 100 demo fetch
│   ├── data_quality_report.py           # Day 1: AMFI code integrity validator
│   ├── data_cleaning.py                 # Day 2: Forward-fill, dedup, validation
│   ├── db_loader.py                     # Day 2: SQLite database loader
│   ├── etl_pipeline.py                  # Master ETL orchestrator (all phases)
│   ├── compute_metrics.py               # Day 4: CAGR, Sharpe, Sortino, Alpha/Beta
│   ├── recommender.py                   # Day 6: Rule-based fund recommendation CLI
│   ├── generate_report.py               # Day 7: Automated PDF report generator
│   └── generate_presentation.py         # Day 7: Automated PPTX deck generator
└── project_description/                 # Capstone task cards & architecture diagrams
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git
- Power BI Desktop (for `.pbix` dashboard viewing)

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

### 3. Run the Full ETL Pipeline
The master orchestrator runs all 4 phases (ingestion → cleaning → database loading → quality audit) in sequence with phase-by-phase logging:
```bash
python scripts/etl_pipeline.py
```
**Outputs:**
- `data/raw/` — Copies of all 10 source CSVs
- `data/processed/` — Cleaned CSVs (`clean_nav.csv`, `clean_transactions.csv`, `clean_performance.csv`)
- `data/db/bluestock_mf.db` — SQLite database with 8 normalized tables
- `reports/etl_pipeline.log` — Full pipeline execution log
- `reports/data_ingestion_summary.txt` — Per-dataset profiling report
- `reports/data_quality_report.md` — AMFI code integrity audit

### 4. Fetch Live NAV Data
Fetches latest NAV data from `api.mfapi.in` for 6 target schemes:
```bash
python scripts/live_nav_fetch.py
```
**Outputs:** `data/raw/raw_nav_{amfi_code}.csv` — 6 CSV files

### 5. Compute Performance & Risk Metrics
Generates CAGR, Sharpe, Sortino, Alpha/Beta, Max Drawdown, and composite fund scorecards:
```bash
python scripts/compute_metrics.py
```
**Outputs:**
- `data/processed/cagr_report.csv`
- `data/processed/fund_scorecard.csv`
- `data/processed/var_cvar_report.csv`

### 6. Run the Fund Recommender
A CLI tool that recommends top-3 funds by Sharpe Ratio based on investor risk appetite:
```bash
python scripts/recommender.py --risk Moderate
python scripts/recommender.py --risk High
python scripts/recommender.py --risk Low
```

### 7. Explore Notebooks
Open Jupyter notebooks for interactive EDA, performance analytics, and advanced risk analysis:
```bash
jupyter notebook notebooks/
```
| Notebook | Focus |
|----------|-------|
| `01_data_ingestion.ipynb` | Dataset profiling, live NAV fetch, AMFI code validation |
| `02_data_cleaning.ipynb` | Cleaning pipeline, SQLite verification, query execution |
| `03_eda_analysis.ipynb` | 15+ EDA visualizations with business insights |
| `04_performance_analytics.ipynb` | Risk-adjusted returns, fund scorecard, benchmarking |
| `05_advanced_analytics.ipynb` | VaR/CVaR, rolling Sharpe, HHI, cohort analysis |

### 8. Generate Final Deliverables
Automatically generate the PDF business report and PowerPoint presentation:
```bash
python scripts/generate_report.py        # → reports/Final_Report.pdf (15–20 pages)
python scripts/generate_presentation.py  # → reports/Presentation.pptx (12 slides)
```

---

## Key Metrics & Formulas

| Metric | Formula | Parameters |
|--------|---------|------------|
| **CAGR** | `(End_NAV / Start_NAV)^(1/years) - 1` | Computed over 1, 3, and 5-year periods |
| **Sharpe Ratio** | `(Return - Rf) / σ` | Rf = 6.5% (India 10yr yield), annualized |
| **Sortino Ratio** | `(Return - Rf) / σ_downside` | Only negative returns in denominator |
| **Alpha / Beta** | OLS regression vs Nifty 100 | `scipy.stats.linregress` |
| **Max Drawdown** | `max(1 - NAV / cummax(NAV))` | Peak-to-trough decline |
| **Composite Score** | Weighted percentile rank | 30% CAGR + 25% Sharpe + 20% Alpha + 15% Expense⁻¹ + 10% MaxDD⁻¹ |

---

## Tech Stack
- **Python** · Pandas · NumPy · Matplotlib · Seaborn · Plotly
- **SQLAlchemy** · SQLite
- **Requests** · SciPy · ReportLab · python-pptx
- **Power BI Desktop** (Dashboard)
- **Git / GitHub** (Version Control)

---

## Author
Kunal Gupta — Capstone Intern, Bluestock Fintech (June–July 2026)
