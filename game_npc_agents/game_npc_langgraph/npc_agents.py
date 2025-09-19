from langchain_openai import ChatOpenAI

# 定义NPC人设
npc_profiles = {
    "村长": "你是村长，年长智慧，喜欢讲故事和建议。",
    "铁匠": "你是铁匠，擅长打造和修理武器，说话粗犷。",
    "药师": "你是药师，懂得草药和治疗，语气温和。"
}

llm = ChatOpenAI(model="gpt-4o-mini")  # 可以换成 gpt-4o

def npc_node(npc_name: str):
    """返回一个NPC节点函数"""
    def node(state):
        user_input = state["input"]
        resp = llm.invoke([
            {"role": "system", "content": npc_profiles[npc_name]},
            {"role": "user", "content": user_input}
        ])
        return {"output": f"{npc_name}: {resp.content}"}
    return node
