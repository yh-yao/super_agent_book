import os, json, glob, re, time
import numpy as np
import faiss
from typing import List, Tuple, Dict
from .llm import embed_texts

VSTORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vectorstore")
CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ingest", "corpus")

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
TOP_K = int(os.getenv("TOP_K","6"))

def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0: start = 0
        if start >= len(text): break
    return chunks

def _load_corpus() -> List[Dict]:
    files = glob.glob(os.path.join(CORPUS_DIR, "*.*"))
    out = []
    for fp in files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        title = os.path.basename(fp)
        # try extract "Effective date" and "Source" for demo
        m_date = re.search(r"Effective date:\s*([0-9\-]+)", txt)
        date = m_date.group(1) if m_date else None
        m_src = re.search(r"Source:\s*(.*)$", txt, re.MULTILINE)
        src = m_src.group(1).strip() if m_src else None
        chunks = _split_text(txt)
        for i, ch in enumerate(chunks):
            out.append({
                "title": title,
                "date": date,
                "url": src,
                "chunk_id": f"{title}#chunk{i}",
                "text": ch
            })
    return out

def _paths():
    return (
        os.path.join(VSTORE_DIR, "index.faiss"),
        os.path.join(VSTORE_DIR, "docs.json")
    )

def build_or_load():
    faiss_path, docs_path = _paths()
    if os.path.exists(faiss_path) and os.path.exists(docs_path):
        index = faiss.read_index(faiss_path)
        with open(docs_path, "r", encoding="utf-8") as f:
            docs = json.load(f)
        return index, docs

    docs = _load_corpus()
    texts = [d["text"] for d in docs]
    embs = embed_texts(texts)
    dim = len(embs[0])
    index = faiss.IndexFlatIP(dim)
    # Normalize for cosine similarity via inner product
    vecs = np.array(embs).astype("float32")
    # L2 normalize
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-10
    vecs = vecs / norms
    index.add(vecs)

    faiss_path, docs_path = _paths()
    faiss.write_index(index, faiss_path)
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    return index, docs

def search(query: str, k: int = TOP_K) -> List[Dict]:
    index, docs = build_or_load()
    q_emb = embed_texts([query])[0]
    q = np.array([q_emb]).astype("float32")
    q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-10)
    D, I = index.search(q, k)
    hits = []
    for idx, score in zip(I[0], D[0]):
        if idx == -1: continue
        d = dict(docs[idx])
        d["score"] = float(score)
        hits.append(d)
    return hits
