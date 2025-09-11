from typing import Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

INTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是企业级客服路由器。根据用户话语判定意图与槽位。意图只在 {labels} 中选择。输出JSON。"),
    ("human", "{query}")
])

def build_intent_chain(labels=("FAQ","TICKET","COMPLAINT","ESCALATION")):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = (INTENT_PROMPT | llm | StrOutputParser())
    return chain, labels

def build_rag_chain(index_name:str):
    retriever = PineconeVectorStore.from_existing_index(
        index_name=index_name, embedding=OpenAIEmbeddings(model="text-embedding-3-large")
    ).as_retriever(search_kwargs={"k":4})
    RAG_PROMPT = ChatPromptTemplate.from_messages([
        ("system", "你是企业FAQ助手。结合检索到的片段逐条引用出处进行回答。若无依据则坦诚告知并建议转工单。"),
        ("human", "问题：{query}\n\n检索结果：{contexts}")
    ])
    def fetch_ctx(x:Dict[str,Any]):
        docs = retriever.get_relevant_documents(x["query"])
        cites = "\n\n".join([f"[{i+1}] {d.page_content[:300]} (source={d.metadata.get('source')}, chunk={d.metadata.get('chunk_id')})" for i,d in enumerate(docs)])
        return {"query": x["query"], "contexts": cites}
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = (RunnablePassthrough()
            | RunnableLambda(fetch_ctx)
            | RAG_PROMPT
            | llm
            | StrOutputParser())
    return chain

def build_router(index_name:str):
    intent_chain, labels = build_intent_chain(labels=("FAQ","TICKET","COMPLAINT","ESCALATION"))
    rag_chain = build_rag_chain(index_name)

    def route(payload):
        import json
        intent_json = intent_chain.invoke({"query": payload["query"], "labels": list(labels)})
        try:
            info = json.loads(intent_json)
            intent = info.get("intent","FAQ")
            slots  = info.get("slots",{})
        except Exception:
            intent, slots = "FAQ", {}

        if intent == "FAQ":
            answer = rag_chain.invoke({"query": payload["query"]})
            return {"intent": intent, "slots": slots, "answer": answer, "actions": []}
        elif intent in ("TICKET","COMPLAINT","ESCALATION"):
            return {"intent": intent, "slots": slots, "answer": None, "actions": ["create_or_update_ticket"]}
        else:
            return {"intent": "FAQ", "slots": slots, "answer": rag_chain.invoke({"query": payload["query"]}), "actions": []}

    return RunnableLambda(route)
