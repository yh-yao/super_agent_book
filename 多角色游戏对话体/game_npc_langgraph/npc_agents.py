from langchain_openai import ChatOpenAI

# 定义NPC人设
npc_profiles = {
    "村长": """你是村长，年长智慧，喜欢讲故事和建议。
当有人问村里有哪些NPC时，你会介绍村里的三位主要居民：
1. 村长（就是你自己）- 负责村庄管理和提供建议
2. 铁匠 - 擅长打造和修理武器装备
3. 药师 - 懂得草药和治疗，帮助村民解决健康问题
只介绍这三位，不要编造其他角色。

重要：直接回复内容，不要在回复前加"村长:"等角色标识。""",
    "铁匠": """你是铁匠，擅长打造和修理武器，说话粗犷。你专注于武器装备相关的话题。

重要：直接回复内容，不要在回复前加"铁匠:"等角色标识。""",
    "药师": """你是药师，懂得草药和治疗，语气温和。你专注于健康和治疗相关的话题。

重要：直接回复内容，不要在回复前加"药师:"等角色标识。"""
}

llm = ChatOpenAI(model="gpt-4o-mini")  # 可以换成 gpt-4o

def npc_node(npc_name: str):
    """返回一个NPC节点函数"""
    def node(state):
        user_input = state["input"]
        chat_history = state.get("chat_history", [])
        
        # 构建包含历史记录的消息
        messages = [{"role": "system", "content": npc_profiles[npc_name]}]
        
        # 添加历史对话（最近10轮，避免token过多）
        if chat_history:
            recent_history = chat_history[-20:]  # 最近10轮对话（用户+助手各10条）
            messages.extend(recent_history)
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        resp = llm.invoke(messages)
        return {"output": f"{npc_name}: {resp.content}"}
    return node
