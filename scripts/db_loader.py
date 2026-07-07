"""
Day 2 — DB Loader
===============================
Initialises the SQLite DB and loads all dimensional and fact tables.
"""

import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------------------
sys.path.append(str(Path(__file__).resolve().parent))
import config

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
logger = logging.getLogger("DBLoader")


def load_database():
    logger.info("-" * 60)
    logger.info("Initializing SQLite database...")
    db_path = config.DB_PATH
    engine = create_engine(f"sqlite:///{db_path}")
    
    # 1. Execute schema.sql
    schema_path = config.SQL_DIR / "schema.sql"
    if schema_path.exists():
        with engine.begin() as conn:
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
                # Split by semicolon and execute each statement
                statements = [s.strip() for s in sql_script.split(';') if s.strip()]
                for stmt in statements:
                    conn.execute(text(stmt))
        logger.info(f"Executed schema from {schema_path.name}")
    else:
        logger.error(f"Missing schema file: {schema_path}")
        return

    def load_and_verify(df, table_name):
        logger.info(f"Loading {table_name} ({len(df)} rows)...")
        with engine.begin() as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
            logger.info(f"Verified {table_name}: {result[0]} rows in database.")

    # 2. Load the 3 cleaned datasets
    logger.info("Loading cleaned datasets...")
    
    # clean_performance -> fact_performance
    path_perf = config.DATA_PROCESSED_DIR / "clean_performance.csv"
    if path_perf.exists():
        df_perf = pd.read_csv(path_perf)
        load_and_verify(df_perf, "fact_performance")
        
    # clean_transactions -> fact_transactions
    path_tx = config.DATA_PROCESSED_DIR / "clean_transactions.csv"
    if path_tx.exists():
        df_tx = pd.read_csv(path_tx)
        load_and_verify(df_tx, "fact_transactions")

    # clean_nav -> fact_nav (with daily_return_pct computation)
    path_nav = config.DATA_PROCESSED_DIR / "clean_nav.csv"
    min_date = None
    max_date = None
    if path_nav.exists():
        df_nav = pd.read_csv(path_nav)
        
        # Parse date to extract min and max for dim_date
        df_nav['date_parsed'] = pd.to_datetime(df_nav['date'])
        min_date = df_nav['date_parsed'].min()
        max_date = df_nav['date_parsed'].max()
        df_nav = df_nav.drop(columns=['date_parsed'])
        
        # Sort and compute daily return
        df_nav = df_nav.sort_values(['amfi_code', 'date'])
        df_nav['daily_return_pct'] = df_nav.groupby('amfi_code')['nav'].transform(lambda x: x / x.shift(1) - 1)
        
        load_and_verify(df_nav, "fact_nav")

    # 3. Generate and load dim_date
    if min_date is not None and max_date is not None:
        logger.info("Generating dim_date...")
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        df_date = pd.DataFrame({'date': date_range})
        df_date['date'] = df_date['date'].dt.strftime('%Y-%m-%d')
        df_date['year'] = date_range.year
        df_date['month'] = date_range.month
        df_date['quarter'] = date_range.quarter
        df_date['day_of_week'] = date_range.dayofweek
        df_date['is_weekday'] = np.where(date_range.dayofweek < 5, 1, 0)
        
        load_and_verify(df_date, "dim_date")

    # 4. Load the 7 uncleaned datasets
    logger.info("Loading raw datasets...")
    
    raw_maps = {
        "01_fund_master.csv": "dim_fund",
        "03_aum_by_fund_house.csv": "fact_aum",
        "04_monthly_sip_inflows.csv": "fact_sip_industry",
        "05_category_inflows.csv": "category_inflows",
        "06_industry_folio_count.csv": "industry_folio_count",
        "09_portfolio_holdings.csv": "fact_portfolio",
        "10_benchmark_indices.csv": "benchmark_indices"
    }
    
    for filename, table_name in raw_maps.items():
        path = config.DATA_RAW_DIR / filename
        if path.exists():
            df_raw = pd.read_csv(path)
            load_and_verify(df_raw, table_name)
        else:
            logger.warning(f"File not found: {path}")

    logger.info(f"Database fully loaded at {db_path.name}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("  DAY 2 — DATABASE LOADER START")
    logger.info("=" * 60)
    load_database()
    logger.info("=" * 60)
    logger.info("  DAY 2 — DATABASE LOADER COMPLETE")
    logger.info("=" * 60)

# Git commit message for Day 2:
# git add .
# git commit -m "Day 2: Cleaned data + SQLite DB loaded"
