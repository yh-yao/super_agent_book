import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from loader import load_docs, chunk_docs

load_dotenv()

def main():
    docs = load_docs("data")
    chunks = chunk_docs(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vector_index")
    print(f"Ingested {len(chunks)} chunks into FAISS index.")

if __name__ == "__main__":
    main()
