import os
from typing import List, Dict, Any

class LocalFileSearch:
    """
    Extremely small local text search: scans .txt files under data_dir
    and returns overlapping windows around matched query terms.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def _iter_txt_files(self):
        for root, _, files in os.walk(self.data_dir):
            for f in files:
                if f.lower().endswith(".txt"):
                    yield os.path.join(root, f)

    def search(self, query: str) -> List[Dict[str, Any]]:
        tokens = [t.lower() for t in query.split() if t.strip()]
        results: List[Dict[str, Any]] = []
        for path in self._iter_txt_files():
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
            for idx, line in enumerate(lines, start=1):
                line_l = line.lower()
                if any(tok in line_l for tok in tokens):
                    # capture a short window
                    start = max(1, idx - 1)
                    end = min(len(lines), idx + 1)
                    text = "".join(lines[start-1:end]).strip()
                    results.append({
                        "file": os.path.relpath(path, start=os.path.dirname(self.data_dir)),
                        "start_line": start,
                        "end_line": end,
                        "text": text
                    })
        # de-dup by (file, start, end, text)
        seen = set()
        deduped = []
        for r in results:
            key = (r["file"], r["start_line"], r["end_line"], r["text"])
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        return deduped
