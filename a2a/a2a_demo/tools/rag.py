from typing import List, Dict, Any
from math import log

def _tf(text: str, token: str) -> float:
    return text.lower().count(token.lower())

def _idf(token: str, corpus: List[str]) -> float:
    df = sum(1 for doc in corpus if token.lower() in doc.lower())
    if df == 0:
        return 0.0
    return log(1 + len(corpus) / df)

def rank_snippets(query: str, hits: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    tokens = [t for t in query.split() if t.strip()]
    corpus = [h["text"] for h in hits] or ["_"]
    scored = []
    for h in hits:
        score = 0.0
        for tok in tokens:
            score += _tf(h["text"], tok) * _idf(tok, corpus)
        scored.append((score, h))
    # deterministic sort: score desc, then file, then start_line
    scored.sort(key=lambda x: (-x[0], x[1]["file"], x[1]["start_line"]))
    return [h for _, h in scored[:top_k]]
