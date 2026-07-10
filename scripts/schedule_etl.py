"""
schedule_etl.py — Bonus Challenge B1: ETL Scheduler Daemon
Runs the live NAV fetch and ETL pipeline automatically every weekday at 8 PM (20:00).
Provides dual scheduling modes:
1. Active background daemon in Python
2. Automatic generation of Windows Task Scheduler / Linux crontab scripts
"""
import sys
import os
import time
from datetime import datetime, timedelta
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def run_pipeline():
    print(f"\n[{datetime.now()}] Starting scheduled ETL pipeline execution...")
    # Exec live_nav_fetch
    fetch_path = BASE_DIR / "scripts" / "live_nav_fetch.py"
    subprocess.run([sys.executable, str(fetch_path)], cwd=str(BASE_DIR))
    
    # Exec etl_pipeline
    pipeline_path = BASE_DIR / "scripts" / "etl_pipeline.py"
    subprocess.run([sys.executable, str(pipeline_path)], cwd=str(BASE_DIR))
    print(f"[{datetime.now()}] Scheduled ETL pipeline execution finished successfully.\n")


def generate_scheduler_configs():
    """Write shell/cmd files to register the cron task in the OS."""
    # Windows Task Scheduler XML/Cmd
    cmd_path = BASE_DIR / "scripts" / "register_windows_task.bat"
    batch_content = f"""@echo off
echo Registering Bluestock MF ETL Scheduler Task (Every Weekday at 8:00 PM)...
schtasks /create /tn "Bluestock_MF_ETL_Pipeline" /tr "{sys.executable} {BASE_DIR}\\scripts\\schedule_etl.py --once" /sc weekly /d MON,TUE,WED,THU,FRI /st 20:00 /ru "SYSTEM"
pause
"""
    cmd_path.write_text(batch_content, encoding="utf-8")
    print(f"Generated Windows registration script: {cmd_path}")

    # Linux Crontab file
    cron_path = BASE_DIR / "scripts" / "register_cron.sh"
    cron_content = f"""# Add this to your crontab using 'crontab -e':
# 0 20 * * 1-5 {sys.executable} {BASE_DIR}/scripts/schedule_etl.py --once >> {BASE_DIR}/reports/cron_execution.log 2>&1
"""
    cron_path.write_text(cron_content, encoding="utf-8")
    print(f"Generated Linux crontab instructions: {cron_path}")


def daemon_loop():
    print("ETL Scheduler Daemon started in active background loop.")
    print("Checking time to match target scheduling (Mon-Fri at 20:00)...")
    while True:
        now = datetime.now()
        # Weekdays: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4
        if now.weekday() < 5 and now.hour == 20 and now.minute == 0:
            run_pipeline()
            # Sleep 65 seconds to avoid double trigger
            time.sleep(65)
        time.sleep(30)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_pipeline()
    else:
        generate_scheduler_configs()
        # Start daemon by default
        try:
            daemon_loop()
        except KeyboardInterrupt:
            print("\nScheduler Daemon stopped by user.")
