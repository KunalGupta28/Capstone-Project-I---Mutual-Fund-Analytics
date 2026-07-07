"""
etl_pipeline.py — Master ETL Orchestration Script
Runs the full pipeline: data ingestion → cleaning → db loading
Logs each phase to reports/etl_pipeline.log
"""
import sys
import logging
import time
from pathlib import Path

# Ensure scripts/ is importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
sys.path.insert(0, str(BASE_DIR / "src"))

from config import REPORTS_DIR

# ── Logging Setup ─────────────────────────────────────────────────────────────
log_file = REPORTS_DIR / "etl_pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ETL] %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ETL")


def run_phase(name: str, module_path: str, func_name: str = "main") -> bool:
    """Dynamically import and run a pipeline phase."""
    logger.info(f"{'='*60}")
    logger.info(f"Starting Phase: {name}")
    t0 = time.time()
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, func_name):
            getattr(mod, func_name)()
        elapsed = time.time() - t0
        logger.info(f"✅ Phase '{name}' completed in {elapsed:.1f}s")
        return True
    except Exception as e:
        logger.error(f"❌ Phase '{name}' failed: {e}", exc_info=True)
        return False


def main():
    logger.info("=" * 60)
    logger.info("BLUESTOCK MF CAPSTONE — ETL PIPELINE STARTED")
    logger.info("=" * 60)

    scripts_dir = BASE_DIR / "scripts"
    src_dir = BASE_DIR / "src"

    # Resolve script paths (prefer scripts/, fall back to src/)
    def resolve(filename):
        p = scripts_dir / filename
        if p.exists():
            return str(p)
        return str(src_dir / filename)

    phases = [
        ("Data Ingestion",    resolve("data_ingestion.py"),    "main"),
        ("Data Cleaning",     resolve("data_cleaning.py"),     "main"),
        ("Database Loader",   resolve("db_loader.py"),         "main"),
        ("Data Quality",      resolve("data_quality_report.py"), "main"),
    ]

    results = {}
    for phase_name, path, func in phases:
        ok = run_phase(phase_name, path, func)
        results[phase_name] = "✅ PASSED" if ok else "❌ FAILED"

    logger.info("=" * 60)
    logger.info("ETL PIPELINE SUMMARY")
    logger.info("=" * 60)
    for phase, status in results.items():
        logger.info(f"  {status}  {phase}")

    failed = [k for k, v in results.items() if "FAILED" in v]
    if failed:
        logger.error(f"Pipeline completed with {len(failed)} failure(s).")
        sys.exit(1)
    else:
        logger.info("All phases completed successfully. ✅")


if __name__ == "__main__":
    main()
