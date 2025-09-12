# utils/audit.py
import json
import time
import os
from datetime import datetime

AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "logs/audit.log")
os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)

def write_audit(entry: dict):
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
