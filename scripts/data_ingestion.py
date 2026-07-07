"""
Day 1 — Data Ingestion Pipeline
================================
Loads all 10 provided CSV datasets, prints shape, dtypes, null counts,
duplicate counts, and head() for each.  Explores fund_master for unique
fund houses, categories, sub-categories, and risk grades.
Generates reports/data_ingestion_summary.txt
"""

import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------------------
sys.path.append(str(Path(__file__).resolve().parent))
import config  # noqa: E402  — must come after sys.path patch
from data_quality_report import audit_datasets

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
log_file = config.REPORTS_DIR / "etl_pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("DataIngestion")


# ---------------------------------------------------------------------------
# Step 1 — Copy raw datasets into data/raw/
# ---------------------------------------------------------------------------
def setup_raw_data():
    """Copies the 10 source CSVs from data_sets/ into data/raw/."""
    logger.info("Initializing raw data layout ...")
    if not config.SOURCE_DATASETS_DIR.exists():
        logger.error(f"Source folder not found: {config.SOURCE_DATASETS_DIR}")
        return
    for src_file in sorted(config.SOURCE_DATASETS_DIR.glob("*.csv")):
        dst_file = config.DATA_RAW_DIR / src_file.name
        if not dst_file.exists():
            shutil.copy(src_file, dst_file)
            logger.info(f"  Copied {src_file.name} -> data/raw/")
        else:
            logger.info(f"  {src_file.name} already in data/raw/ (skipped)")


# ---------------------------------------------------------------------------
# Step 2 — Load every dataset, print shape / dtypes / nulls / duplicates / head
# ---------------------------------------------------------------------------
def analyze_datasets():
    """Loads each CSV in data/raw/ and writes a per-dataset profile."""
    setup_raw_data()

    raw_files = sorted(config.DATA_RAW_DIR.glob("[0-9]*.csv"))  # only the 10 numbered datasets
    if not raw_files:
        logger.warning("No numbered CSV files found in data/raw/")
        return

    summary_path = config.REPORTS_DIR / "data_ingestion_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"{'=' * 60}\n")
        f.write(f"  Day 1 — Data Ingestion Summary\n")
        f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 60}\n\n")

        for fp in raw_files:
            logger.info("-" * 60)
            logger.info(f"Processing: {fp.name}")
            try:
                df = pd.read_csv(fp)

                shape = df.shape
                dtypes = df.dtypes
                nulls = df.isnull().sum()
                total_nulls = nulls.sum()
                duplicates = df.duplicated().sum()
                head = df.head(5)

                # ---- Console output (matches Day 1 requirement) ----
                logger.info(f"  Shape       : {shape}")
                logger.info(f"  Columns     : {list(df.columns)}")
                logger.info(f"  Duplicates  : {duplicates}")
                logger.info(f"  Total Nulls : {total_nulls}")

                # ---- Anomaly notes ----
                anomalies = []
                if total_nulls > 0:
                    null_cols = nulls[nulls > 0].to_dict()
                    anomalies.append(f"Null values found: {null_cols}")
                if duplicates > 0:
                    anomalies.append(f"{duplicates} duplicate row(s) detected")

                # ---- Write to report file ----
                block = (
                    f"Dataset : {fp.name}\n"
                    f"Shape   : {shape}\n"
                    f"Columns : {list(df.columns)}\n\n"
                    f"Data Types:\n{dtypes.to_string()}\n\n"
                    f"Null Counts:\n{nulls.to_string()}\n\n"
                    f"Duplicate Rows: {duplicates}\n\n"
                    f"Sample Rows (head):\n{head.to_string()}\n\n"
                )
                if anomalies:
                    block += "Anomalies Noted:\n"
                    for a in anomalies:
                        block += f"  [!] {a}\n"
                    block += "\n"
                block += f"{'=' * 60}\n\n"
                f.write(block)

            except Exception as e:
                logger.error(f"  FAILED to process {fp.name}: {e}")

    logger.info("-" * 60)
    logger.info(f"Summary saved -> {summary_path}")


# ---------------------------------------------------------------------------
# Step 3 — Explore fund_master structure
# ---------------------------------------------------------------------------
def explore_fund_master():
    """Prints unique fund houses, categories, sub-categories, and risk grades."""
    master_path = config.DATA_RAW_DIR / "01_fund_master.csv"
    if not master_path.exists():
        logger.warning("01_fund_master.csv not found in data/raw/")
        return

    df = pd.read_csv(master_path)

    logger.info("=" * 60)
    logger.info("Fund Master Exploration")
    logger.info("=" * 60)

    logger.info(f"\nUnique Fund Houses ({df['fund_house'].nunique()}):")
    for fh in sorted(df["fund_house"].unique()):
        logger.info(f"  - {fh}")

    logger.info(f"\nUnique Categories ({df['category'].nunique()}):")
    for cat in sorted(df["category"].unique()):
        logger.info(f"  - {cat}")

    logger.info(f"\nUnique Sub-Categories ({df['sub_category'].nunique()}):")
    for sub in sorted(df["sub_category"].unique()):
        logger.info(f"  - {sub}")

    logger.info(f"\nUnique Risk Categories ({df['risk_category'].nunique()}):")
    for rc in sorted(df["risk_category"].unique()):
        logger.info(f"  - {rc}")

    logger.info(f"\nTotal Schemes : {len(df)}")
    logger.info(f"AMFI Codes    : {sorted(df['amfi_code'].tolist())}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("  DAY 1 — DATA INGESTION PIPELINE START")
    logger.info("=" * 60)
    analyze_datasets()
    explore_fund_master()
    
    logger.info("=" * 60)
    logger.info("  DAY 1 — TASK 7: DATA QUALITY AUDIT")
    logger.info("=" * 60)
    audit_datasets()
    
    logger.info("=" * 60)
    logger.info("  DAY 1 — DATA INGESTION PIPELINE COMPLETE")
    logger.info("=" * 60)
