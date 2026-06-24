import sys
import logging
from datetime import date
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent))
import config

logger = logging.getLogger("DataQualityAuditor")
if not logger.handlers:
    log_file = config.REPORTS_DIR / "etl_pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def audit_datasets():
    """Performs data quality checks, specifically validating AMFI codes between master and NAV records."""
    logger.info("Starting Data Quality Audit...")
    
    master_path = config.DATA_RAW_DIR / "01_fund_master.csv"
    nav_path = config.DATA_RAW_DIR / "02_nav_history.csv"
    
    if not master_path.exists() or not nav_path.exists():
        logger.error("Missing core datasets (01_fund_master.csv or 02_nav_history.csv) for validation.")
        return
        
    try:
        # Load datasets
        master_df = pd.read_csv(master_path)
        nav_df = pd.read_csv(nav_path)
        
        # Unique AMFI codes in both tables
        master_codes = set(master_df["amfi_code"].unique())
        nav_codes = set(nav_df["amfi_code"].unique())
        
        total_master_schemes = len(master_codes)
        total_nav_schemes = len(nav_codes)
        
        # Check overlaps
        matching_codes = master_codes.intersection(nav_codes)
        missing_in_nav = master_codes - nav_codes
        extra_in_nav = nav_codes - master_codes
        
        # Construct Markdown audit report
        report_path = config.REPORTS_DIR / "data_quality_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Bluestock Mutual Fund Analytics - Data Quality Audit Report\n\n")
            f.write(f"**Date of Audit**: {date.today()}\n")
            f.write(f"**Audit Status**: {'WARNING' if missing_in_nav else 'PASSED'}\n\n")
            
            f.write("## 1. Key Metrics Summary\n")
            f.write(f"- **Total Schemes in Fund Master**: {total_master_schemes}\n")
            f.write(f"- **Total Schemes in NAV History**: {total_nav_schemes}\n")
            f.write(f"- **Matching Schemes (Overlapping)**: {len(matching_codes)}\n")
            f.write(f"- **Master Schemes Missing NAV History**: {len(missing_in_nav)}\n")
            f.write(f"- **Extra Schemes in NAV History (Not in Master)**: {len(extra_in_nav)}\n\n")
            
            f.write("## 2. Integrity Analysis\n")
            if missing_in_nav:
                f.write("### Warning: Master Schemes Missing NAV History\n")
                f.write("The following AMFI codes are registered in the master database but have no pricing data in the NAV history:\n\n")
                f.write("| AMFI Code | Scheme Name | Fund House |\n")
                f.write("| :--- | :--- | :--- |\n")
                for code in sorted(missing_in_nav):
                    row = master_df[master_df["amfi_code"] == code].iloc[0]
                    f.write(f"| {code} | {row['scheme_name']} | {row['fund_house']} |\n")
                f.write("\n")
            else:
                f.write("✔ **Referential Integrity Check Passed**: All AMFI codes in `fund_master` possess corresponding daily NAV history rows.\n\n")
                
            if extra_in_nav:
                f.write("### Info: Extra Schemes in NAV History (Orphaned Pricing)\n")
                f.write("These codes exist in `nav_history` but have no corresponding details in `fund_master`:\n\n")
                for code in sorted(extra_in_nav):
                    f.write(f"- AMFI Code: {code}\n")
                f.write("\n")
                
        logger.info(f"Data quality audit completed. Report written to {report_path.name}")
        logger.info(f"Status: Matching: {len(matching_codes)} | Missing in NAV: {len(missing_in_nav)}")
        
    except Exception as e:
        logger.error(f"Audit execution crashed: {str(e)}")

if __name__ == "__main__":
    audit_datasets()
