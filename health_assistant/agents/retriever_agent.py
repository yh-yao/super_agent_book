from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

class RetrieverAgent:
    def __init__(self, index_path="medical_index"):
        self.db = FAISS.load_local(index_path, OpenAIEmbeddings())

    def run(self, query):
        docs = self.db.similarity_search(query, k=3)
        return [d.page_content for d in docs]
