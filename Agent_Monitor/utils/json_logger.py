# Agent_Monitor/utils/json_logger.py
import os
import json
from datetime import datetime
from typing import Any, Dict

def save_json(obj: Dict[str, Any], filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def timestamped_path(dirpath: str, prefix: str = "run", ext: str = ".json"):
    os.makedirs(dirpath, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(dirpath, f"{prefix}_{ts}{ext}")
