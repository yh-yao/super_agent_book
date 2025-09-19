
import os, io, csv, statistics
from typing import Dict, Any, List

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def save_upload(upload_dir: str, filename: str, data: bytes) -> str:
    ensure_dir(upload_dir)
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path

def csv_basic_stats(path: str) -> Dict[str, Dict[str, float]]:
    stats = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows: return stats
        cols = reader.fieldnames or []
        for c in cols:
            vals = []
            for r in rows:
                try:
                    vals.append(float(r[c]))
                except Exception:
                    pass
            if vals:
                stats[c] = {
                    "count": float(len(vals)),
                    "mean": float(sum(vals)/len(vals)),
                    "stdev": float(statistics.pstdev(vals)) if len(vals)>1 else 0.0,
                    "min": float(min(vals)),
                    "max": float(max(vals)),
                }
    return stats
