#!/usr/bin/env python3
"""
Continuous health monitoring for Chemistry AI Tutor
Run as: nohup python3 monitoring/health_check.py &
"""

import requests
import time
import logging
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
CHECK_INTERVAL = 60  # seconds
LOG_FILE = "/var/log/chemistry-ai-health.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def check_backend_health():
    """Check if backend is responding"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Backend healthy - Chunks: {data.get('db_chunks', 'N/A')}")
            return True
        else:
            logging.error(f"Backend unhealthy - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Backend check failed: {e}")
        return False

def check_disk_space():
    """Check if disk space is sufficient"""
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    percent_used = (used / total) * 100

    if free_gb < 1:
        logging.warning(f"Low disk space: {free_gb}GB free")
        return False
    elif percent_used > 90:
        logging.warning(f"Disk usage high: {percent_used:.1f}%")
        return False
    else:
        logging.info(f"Disk space OK: {free_gb}GB free ({percent_used:.1f}% used)")
        return True

def main():
    """Main monitoring loop"""
    logging.info("Starting health monitoring...")
    consecutive_failures = 0

    while True:
        try:
            # Check backend
            backend_healthy = check_backend_health()

            # Check disk space (every 10 checks)
            if int(time.time()) % 600 == 0:
                check_disk_space()

            # Track failures
            if not backend_healthy:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    logging.critical(f"Backend down for {consecutive_failures} checks!")
                    # TODO: Send alert (email, Slack, etc.)
            else:
                consecutive_failures = 0

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            break
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
