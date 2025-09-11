import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from loader import load_and_chunk

load_dotenv()
index_name = os.getenv("PINECONE_INDEX")

def main():
    docs = load_and_chunk("data")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    texts = [c for c,_ in docs]
    metadatas = [m for _,m in docs]
    PineconeVectorStore.from_texts(texts=texts, embedding=embeddings, index_name=index_name, metadatas=metadatas)
    print(f"Ingested {len(texts)} chunks into {index_name}")

if __name__ == "__main__":
    main()
