from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS

def build_doc_qa(index_dir="vector_index"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k":4})

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是企业文档助手，根据检索到的文档片段回答问题，并在答案中引用出处。"),
        ("human", "{query}\n\n历史对话：{history}")
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )
    return qa
