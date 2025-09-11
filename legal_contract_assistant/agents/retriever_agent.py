from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

class RetrieverAgent:
    def __init__(self, index_path="law_index"):
        self.db = FAISS.load_local(index_path, OpenAIEmbeddings())

    def run(self, clause_text):
        docs = self.db.similarity_search(clause_text, k=2)
        return [d.page_content for d in docs]
