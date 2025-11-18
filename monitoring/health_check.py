#!/usr/bin/env python3
"""
Continuous health monitoring for Chemistry AI Tutor
Run as: nohup python3 monitoring/health_check.py &
"""

import requests
import time
import logging
import os
import json
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds
LOG_FILE = os.getenv("LOG_FILE", "/var/log/chemistry-ai-health.log")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Optional Slack webhook for alerts

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

def send_slack_alert(message: str, severity: str = "warning"):
    """Send alert to Slack webhook"""
    if not SLACK_WEBHOOK_URL:
        logging.debug("Slack webhook not configured - skipping alert")
        return False

    try:
        # Color codes for different severities
        colors = {
            "critical": "#dc2626",  # red
            "warning": "#f59e0b",   # yellow
            "info": "#3b82f6"       # blue
        }

        payload = {
            "attachments": [{
                "color": colors.get(severity, "#f59e0b"),
                "title": "🧪 Chemistry AI Tutor Alert",
                "text": message,
                "footer": "Health Monitoring",
                "ts": int(datetime.now().timestamp())
            }]
        }

        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=5
        )

        if response.status_code == 200:
            logging.info(f"Slack alert sent: {message[:50]}...")
            return True
        else:
            logging.error(f"Failed to send Slack alert: {response.status_code}")
            return False

    except Exception as e:
        logging.error(f"Error sending Slack alert: {e}")
        return False

def main():
    """Main monitoring loop"""
    logging.info("Starting health monitoring...")
    if SLACK_WEBHOOK_URL:
        logging.info("Slack alerts enabled")
        send_slack_alert("Health monitoring started", "info")
    else:
        logging.info("Slack alerts disabled (SLACK_WEBHOOK_URL not set)")

    consecutive_failures = 0
    alert_sent = False  # Track if we've already sent an alert

    while True:
        try:
            # Check backend
            backend_healthy = check_backend_health()

            # Check disk space (every 10 checks)
            if int(time.time()) % 600 == 0:
                disk_healthy = check_disk_space()
                if not disk_healthy and SLACK_WEBHOOK_URL:
                    send_slack_alert(
                        "⚠️ Low disk space detected on Chemistry AI Tutor server",
                        "warning"
                    )

            # Track failures
            if not backend_healthy:
                consecutive_failures += 1
                if consecutive_failures >= 3 and not alert_sent:
                    error_msg = f"🚨 Backend has failed {consecutive_failures} consecutive health checks!"
                    logging.critical(error_msg)

                    # Send Slack alert
                    send_slack_alert(
                        f"{error_msg}\n"
                        f"Backend URL: {BACKEND_URL}\n"
                        f"Time: {datetime.now().isoformat()}\n"
                        f"Please investigate immediately.",
                        "critical"
                    )
                    alert_sent = True

            else:
                # Backend recovered
                if alert_sent and consecutive_failures > 0:
                    recovery_msg = f"✅ Backend recovered after {consecutive_failures} failed checks"
                    logging.info(recovery_msg)
                    send_slack_alert(recovery_msg, "info")

                consecutive_failures = 0
                alert_sent = False

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            send_slack_alert("Health monitoring stopped", "info")
            break
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
