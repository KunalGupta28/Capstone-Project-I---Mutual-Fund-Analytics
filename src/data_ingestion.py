import sys
import shutil
import logging
import pandas as pd
from pathlib import Path

# Add src to system path to ensure proper module discovery
sys.path.append(str(Path(__file__).resolve().parent))
import config

# Set up logging to reports/etl_pipeline.log and Console
log_file = config.REPORTS_DIR / "etl_pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DataIngestion")

def setup_raw_data():
    """Copies source CSV files from data_sets directory into data/raw/."""
    logger.info("Initializing raw data layout...")
    
    if not config.SOURCE_DATASETS_DIR.exists():
        logger.error(f"Source datasets folder not found at {config.SOURCE_DATASETS_DIR}")
        return
        
    for source_file in config.SOURCE_DATASETS_DIR.glob("*.csv"):
        dest_file = config.DATA_RAW_DIR / source_file.name
        if not dest_file.exists():
            shutil.copy(source_file, dest_file)
            logger.info(f"Copied {source_file.name} to data/raw/")
        else:
            logger.debug(f"{source_file.name} already exists in data/raw/")

def analyze_datasets():
    """Loads all datasets from data/raw/, prints stats, and generates reports/data_ingestion_summary.txt."""
    setup_raw_data()
    
    raw_files = sorted(list(config.DATA_RAW_DIR.glob("*.csv")))
    if not raw_files:
        logger.warning("No CSV files found in data/raw/ to analyze.")
        return
        
    summary_path = config.REPORTS_DIR / "data_ingestion_summary.txt"
    
    with open(summary_path, "w", encoding="utf-8") as summary_file:
        summary_file.write("=== Day 1: Data Ingestion Summary ===\n\n")
        
        for file_path in raw_files:
            logger.info("-" * 50)
            logger.info(f"Processing dataset: {file_path.name}")
            
            try:
                df = pd.read_csv(file_path)
                
                # Compute Statistics
                shape = df.shape
                dtypes = df.dtypes
                nulls = df.isnull().sum()
                duplicates = df.duplicated().sum()
                sample = df.head(2)
                
                # Format output strings
                summary_block = (
                    f"Dataset: {file_path.name}\n"
                    f"Shape: {shape}\n"
                    f"Duplicate Rows: {duplicates}\n"
                    f"Null Counts:\n{nulls.to_string()}\n"
                    f"Data Types:\n{dtypes.to_string()}\n"
                    f"Sample Rows (First 2):\n{sample.to_string()}\n"
                    f"{'='*50}\n\n"
                )
                
                # Write to summary file
                summary_file.write(summary_block)
                
                # Print highlights to log
                logger.info(f"Shape: {shape} | Duplicate count: {duplicates}")
                logger.info(f"Null counts: {nulls.sum()} total null values")
                logger.info(f"Sample data columns: {list(df.columns)}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                
    logger.info("-" * 50)
    logger.info(f"Dataset analysis complete. Summary saved to: {summary_path}")

if __name__ == "__main__":
    analyze_datasets()
