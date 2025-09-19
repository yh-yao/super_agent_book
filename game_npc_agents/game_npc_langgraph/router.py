from langchain_openai import ChatOpenAI

llm_router = ChatOpenAI(model="gpt-4o-mini")

def route_node(state):
    """用LLM决定分配给哪个NPC"""
    user_input = state["input"]

    system_prompt = """你是一个游戏调度器。
根据玩家输入，选择一个或多个NPC来回答。
NPC有：村长、铁匠、药师。
输出用逗号分隔，例如：铁匠 或 铁匠,药师。"""

    resp = llm_router.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ])

    chosen = [npc.strip() for npc in resp.content.split(",")]
    return {"npc_targets": chosen}
