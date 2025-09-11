import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from loader import load_and_chunk

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "helpdesk-knowledge")

def main():
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY must be set in your .env file.")
    
    docs = load_and_chunk(data_dir="data")
    print(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512)
    texts = [c for c, _ in docs]
    metadatas = [m for _, m in docs]
    vectorstore = PineconeVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        index_name=INDEX_NAME,
        pinecone_api_key=PINECONE_API_KEY,
        metadatas=metadatas
    )
    print(f"Ingested {len(texts)} chunks into {INDEX_NAME}")

if __name__ == "__main__":
    main()
