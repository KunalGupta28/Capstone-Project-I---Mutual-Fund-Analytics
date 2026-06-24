import sys
import logging
import requests
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent))
import config

logger = logging.getLogger("HDFCDemo")
# Setup basic logging
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

def fetch_hdfc_demo():
    """Fetches historical and latest NAV data specifically for HDFC Top 100 as the initial demo."""
    logger.info("=" * 60)
    logger.info("  DAY 1 — TASK 4: HDFC TOP 100 DEMO FETCH")
    logger.info("=" * 60)
    
    code, name = list(config.HDFC_NAV_TARGET.items())[0]
    
    url = f"{config.MF_API_BASE_URL}/{code}"
    logger.info(f"Fetching NAV data for {name} (Code: {code}) from {url}...")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Verify JSON schema contains expected keys
        if "data" not in data or "meta" not in data:
            logger.error(f"Malformed API response for scheme {code}")
            return False
            
        nav_records = data["data"]
        meta = data["meta"]
        
        # Convert records list to Pandas DataFrame
        df = pd.DataFrame(nav_records)
        df["amfi_code"] = code
        df["scheme_name"] = meta.get("scheme_name", name)
        
        # Re-order columns: amfi_code, date, nav, scheme_name
        if "date" in df.columns and "nav" in df.columns:
            df = df[["amfi_code", "date", "nav", "scheme_name"]]
        else:
            logger.error(f"Required data columns missing for scheme {code}")
            return False
            
        # Write CSV file to data/raw/
        output_file = config.DATA_RAW_DIR / f"raw_nav_{code}.csv"
        df.to_csv(output_file, index=False)
        
        logger.info(f"Successfully saved {len(df)} NAV records to {output_file.name}")
        logger.info(f"Dataset Head:\n{df.head()}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP connection failed for scheme {code}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to process NAV data for scheme {code}: {str(e)}")
        return False

if __name__ == "__main__":
    fetch_hdfc_demo()
