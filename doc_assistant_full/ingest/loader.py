from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

def load_docs(data_dir="data"):
    docs = []
    for p in Path(data_dir).rglob("*.pdf"):
        loader = PyPDFLoader(str(p))
        docs.extend(loader.load())
    for p in Path(data_dir).rglob("*.txt"):
        text = p.read_text(encoding="utf-8")
        docs.append({"page_content": text, "metadata": {"source": p.name}})
    return docs

def chunk_docs(docs, chunk_size=800, overlap=120):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_documents(docs)
