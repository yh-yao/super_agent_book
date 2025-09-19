
import os, re
from typing import List, Dict

def tokenize(text: str):
    return re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", text.lower())

class TinyVectorStore:
    def __init__(self):
        self.docs: List[Dict] = []

    def _tf(self, text: str) -> Dict[str, int]:
        tf = {}
        for t in tokenize(text):
            tf[t] = tf.get(t, 0) + 1
        return tf

    def add_doc(self, doc_id: str, text: str, source: str):
        self.docs.append({"id": doc_id, "text": text, "tf": self._tf(text), "source": source})

    def _sim(self, qtf: Dict[str,int], dtf: Dict[str,int]) -> float:
        score = 0.0
        for k, v in qtf.items():
            if k in dtf: score += v * dtf[k]
        return float(score)

    def search(self, query: str, top_k: int = 5):
        qtf = self._tf(query)
        scored = []
        for d in self.docs:
            scored.append((self._sim(qtf, d["tf"]), d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"text": d["text"], "source": d["source"], "score": s} for s, d in scored[:top_k]]

def build_demo_store(data_dir: str) -> TinyVectorStore:
    vs = TinyVectorStore()
    if os.path.isdir(data_dir):
        for fn in os.listdir(data_dir):
            p = os.path.join(data_dir, fn)
            if os.path.isfile(p) and fn.endswith(".txt"):
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
                vs.add_doc(fn, txt, source=f"data/{fn}")
    return vs
