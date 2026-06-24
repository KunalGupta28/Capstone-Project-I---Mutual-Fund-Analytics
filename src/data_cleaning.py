"""
Day 2 — Data Cleaning Pipeline
===============================
Cleans NAV history, investor transactions, and scheme performance datasets.
Outputs clean CSV files into data/processed/.
"""

import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np

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
logger = logging.getLogger("DataCleaning")


def clean_nav_history():
    """
    Cleans 02_nav_history.csv -> clean_nav.csv
    - Parse date to datetime
    - Sort by amfi_code then date
    - Reindex to full business day range per fund & forward-fill
    - Remove duplicates
    - Validate nav > 0
    """
    logger.info("-" * 60)
    logger.info("Cleaning NAV History...")
    input_path = config.DATA_RAW_DIR / "02_nav_history.csv"
    output_path = config.DATA_PROCESSED_DIR / "clean_nav.csv"
    
    if not input_path.exists():
        logger.error(f"Missing input file: {input_path}")
        return
        
    df = pd.read_csv(input_path)
    initial_count = len(df)
    
    # Remove complete duplicates
    df = df.drop_duplicates()
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)
    
    # Sort
    df = df.sort_values(by=['amfi_code', 'date']).reset_index(drop=True)
    
    # Validate nav > 0
    invalid_navs = df[df['nav'] <= 0]
    if not invalid_navs.empty:
        logger.warning(f"Found {len(invalid_navs)} rows with NAV <= 0. Dropping them.")
        df = df[df['nav'] > 0]
        
    # Reindex to full business day range per fund and forward-fill
    def reindex_fund(group):
        amfi = group['amfi_code'].iloc[0] if 'amfi_code' in group.columns else group.name
        group = group.set_index('date')
        # Remove duplicate dates within the same fund if any exist
        group = group[~group.index.duplicated(keep='last')]
        if group.empty:
            return group
        min_date = group.index.min()
        max_date = group.index.max()
        idx = pd.bdate_range(start=min_date, end=max_date)
        group = group.reindex(idx)
        group['amfi_code'] = amfi
        group['nav'] = group['nav'].ffill()
        return group.rename_axis('date').reset_index()

    # Apply reindexing and drop any unfillable early NaNs
    df = df.groupby('amfi_code', group_keys=False).apply(reindex_fund).dropna(subset=['nav'])
    
    # Final sort just in case
    df = df.sort_values(by=['amfi_code', 'date']).reset_index(drop=True)
    
    final_count = len(df)
    df = df[['amfi_code', 'date', 'nav']]
    df.to_csv(output_path, index=False)
    
    logger.info(f"NAV History: Processed {initial_count} -> {final_count} rows.")


def clean_investor_transactions():
    """
    Cleans 08_investor_transactions.csv -> clean_transactions.csv
    - Parse transaction_date
    - Standardise transaction_type (SIP, Lumpsum, Redemption)
    - Validate amount_inr > 0
    - Validate kyc_status (Verified, Pending)
    """
    logger.info("-" * 60)
    logger.info("Cleaning Investor Transactions...")
    input_path = config.DATA_RAW_DIR / "08_investor_transactions.csv"
    output_path = config.DATA_PROCESSED_DIR / "clean_transactions.csv"
    
    if not input_path.exists():
        logger.error(f"Missing input file: {input_path}")
        return
        
    df = pd.read_csv(input_path)
    initial_count = len(df)
    
    # Parse dates
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='mixed', dayfirst=True)
    
    # Standardise transaction_type
    df['transaction_type'] = df['transaction_type'].astype(str).str.strip().str.title()
    type_map = {
        'Sip': 'SIP',
        'Lumpsum': 'Lumpsum',
        'Redemption': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].map(type_map).fillna(df['transaction_type'])
    df = df[df['transaction_type'].isin(['SIP', 'Lumpsum', 'Redemption'])]
    
    # Validate amount > 0
    invalid_amounts = df[df['amount_inr'] <= 0]
    if not invalid_amounts.empty:
        logger.warning(f"Found {len(invalid_amounts)} rows with amount <= 0. Dropping them.")
        df = df[df['amount_inr'] > 0]
        
    # Validate kyc_status
    df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.title()
    df = df[df['kyc_status'].isin(['Verified', 'Pending'])]
    
    final_count = len(df)
    df.to_csv(output_path, index=False)
    
    logger.info(f"Investor Transactions: Processed {initial_count} -> {final_count} rows.")


def clean_scheme_performance():
    """
    Cleans 07_scheme_performance.csv -> clean_performance.csv
    - Validate return columns are numeric, coerce errors to NaN
    - Flag negative sharpe_ratio
    - Validate expense_ratio_pct range
    """
    logger.info("-" * 60)
    logger.info("Cleaning Scheme Performance...")
    input_path = config.DATA_RAW_DIR / "07_scheme_performance.csv"
    output_path = config.DATA_PROCESSED_DIR / "clean_performance.csv"
    
    if not input_path.exists():
        logger.error(f"Missing input file: {input_path}")
        return
        
    df = pd.read_csv(input_path)
    initial_count = len(df)
    
    numeric_cols = [
        'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 
        'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio', 
        'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct'
    ]
    
    # Coerce to numeric
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Flag negative sharpe
    if 'sharpe_ratio' in df.columns:
        neg_sharpe = df[df['sharpe_ratio'] < 0]
        if not neg_sharpe.empty:
            logger.warning(f"Found {len(neg_sharpe)} schemes with negative sharpe_ratio.")
            
    # Validate expense ratio range
    if 'expense_ratio_pct' in df.columns:
        df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
        anomalies = df[(df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5)]
        if not anomalies.empty:
            logger.warning(f"Found {len(anomalies)} schemes with expense_ratio_pct outside 0.1% - 2.5%.")
            
    final_count = len(df)
    df.to_csv(output_path, index=False)
    
    logger.info(f"Scheme Performance: Processed {initial_count} -> {final_count} rows.")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("  DAY 2 — DATA CLEANING PIPELINE START")
    logger.info("=" * 60)
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    logger.info("=" * 60)
    logger.info("  DAY 2 — DATA CLEANING PIPELINE COMPLETE")
    logger.info("=" * 60)

# Git commit message for Day 2:
# git add .
# git commit -m "Day 2: Cleaned data + SQLite DB loaded"
