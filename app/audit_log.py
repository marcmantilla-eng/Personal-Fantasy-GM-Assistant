"""Records what the app looked at and recommended, in a plain CSV file.

This is a paper trail, not a database: every entry is one line appended
to logs/audit_log.csv, so you can open it directly in Excel to review
what the assistant examined and suggested over time. Phase 2 only logs
"viewed" events; approval/action logging will be added when write
features exist in a later phase.
"""

import csv
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_PATH = os.path.join(LOG_DIR, "audit_log.csv")

FIELDS = ["timestamp", "event_type", "screen", "summary"]


def log_event(timestamp: str, event_type: str, screen: str, summary: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    is_new = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "timestamp": timestamp,
            "event_type": event_type,
            "screen": screen,
            "summary": summary,
        })
