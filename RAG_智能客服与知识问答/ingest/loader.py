from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_chunk(data_dir="data", chunk_size=800, chunk_overlap=120):
    texts = []
    for p in Path(data_dir).rglob("*"):
        if p.suffix.lower() in [".md", ".txt"]:
            texts.append((p.name, p.read_text(encoding="utf-8")))
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = []
    for name, raw in texts:
        for i, chunk in enumerate(splitter.split_text(raw)):
            metadata = {"source": name, "chunk_id": i}
            docs.append((chunk, metadata))
    return docs
