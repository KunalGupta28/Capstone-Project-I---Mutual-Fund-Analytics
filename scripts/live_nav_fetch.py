import sys
import logging
import requests
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent))
import config

logger = logging.getLogger("LiveNAVFetch")
# Inherit logging setup from data_ingestion if running in pipeline, else setup basic logging
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

def fetch_scheme_nav(scheme_code: str, scheme_name: str):
    """Fetches historical and latest NAV data from api.mfapi.in and saves it as a raw CSV."""
    url = f"{config.MF_API_BASE_URL}/{scheme_code}"
    logger.info(f"Fetching NAV data for {scheme_name} (Code: {scheme_code}) from {url}...")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Verify JSON schema contains expected keys
        if "data" not in data or "meta" not in data:
            logger.error(f"Malformed API response for scheme {scheme_code}")
            return False
            
        nav_records = data["data"]
        meta = data["meta"]
        
        # Convert records list to Pandas DataFrame
        df = pd.DataFrame(nav_records)
        df["amfi_code"] = scheme_code
        df["scheme_name"] = meta.get("scheme_name", scheme_name)
        
        # Re-order columns: amfi_code, date, nav, scheme_name
        if "date" in df.columns and "nav" in df.columns:
            df = df[["amfi_code", "date", "nav", "scheme_name"]]
        else:
            logger.error(f"Required data columns missing for scheme {scheme_code}")
            return False
            
        # Write CSV file to data/raw/
        output_file = config.DATA_RAW_DIR / f"raw_nav_{scheme_code}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Successfully saved {len(df)} NAV records to {output_file.name}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP connection failed for scheme {scheme_code}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to process NAV data for scheme {scheme_code}: {str(e)}")
        return False

def fetch_all_targets():
    """Loops through all target schemes and fetches their NAV data."""
    logger.info("=" * 60)
    logger.info("  DAY 1 — TASK 5: FETCHING 5 KEY SCHEMES NAV")
    logger.info("=" * 60)
    success_count = 0
    
    for code, name in config.LIVE_NAV_TARGETS.items():
        if fetch_scheme_nav(code, name):
            success_count += 1
            
    logger.info(f"Live NAV Fetch job completed. Successfully fetched {success_count}/{len(config.LIVE_NAV_TARGETS)} schemes.")

if __name__ == "__main__":
    from hdfc_nav_demo import fetch_hdfc_demo
    fetch_hdfc_demo()
    fetch_all_targets()