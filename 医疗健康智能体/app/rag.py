import os, glob, json
from typing import List, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .config import DATA_DIR, INDEX_DIR, EMBED_MODEL
from .models import Evidence

@dataclass
class DocChunk:
    doc_id: str
    title: str
    text: str
    source: str

class RAGIndex:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.index = None
        self.chunks: List[DocChunk] = []

    def _load_texts(self) -> List[DocChunk]:
        chunks = []
        for path in glob.glob(os.path.join(DATA_DIR, "*.txt")):
            title = os.path.basename(path)
            source = f"local:{title}"
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read().strip()
            # naive split by paragraphs
            parts = [p.strip() for p in txt.split("\n\n") if p.strip()]
            for i, p in enumerate(parts):
                chunks.append(DocChunk(
                    doc_id=f"{title}#p{i}",
                    title=title,
                    text=p,
                    source=source
                ))
        return chunks

    def build(self):
        self.chunks = self._load_texts()
        vecs = self.embedder.encode([c.text for c in self.chunks], normalize_embeddings=True)
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(np.array(vecs, dtype="float32"))

    def search(self, query: str, k: int = 5) -> List[Evidence]:
        if self.index is None:
            self.build()
        q = self.embedder.encode([query], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q, k)
        out: List[Evidence] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1: 
                continue
            c = self.chunks[int(idx)]
            out.append(Evidence(
                doc_id=c.doc_id, title=c.title, chunk=c.text, score=float(score), source=c.source
            ))
        return out
