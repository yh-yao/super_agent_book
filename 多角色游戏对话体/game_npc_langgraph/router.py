from langchain_openai import ChatOpenAI

llm_router = ChatOpenAI(model="gpt-4o-mini")

def route_node(state):
    """用LLM决定分配给哪个NPC"""
    user_input = state["input"]
    chat_history = state.get("chat_history", [])

    system_prompt = """你是一个游戏调度器。
根据玩家输入和对话历史，选择最合适的NPC来回答。

可选的NPC：
- 村长：负责村庄管理、历史故事、一般建议和信息
- 铁匠：负责武器装备、打造修理、战斗相关
- 药师：负责治疗、草药、健康相关

规则：
1. 只能选择一个NPC
2. 直接输出NPC名字，不要多余的文字
3. 考虑对话上下文，如果之前在和某个NPC聊相关话题，可以继续选择同一个NPC
4. 如果问题涉及多个领域或一般性问题，选择村长

示例：
玩家说"我需要买武器" -> 铁匠
玩家说"我受伤了" -> 药师  
玩家说"这里有什么NPC" -> 村长
玩家说"你好" -> 村长"""

    # 构建包含历史的消息
    messages = [{"role": "system", "content": system_prompt}]
    
    # 添加最近的对话历史（最多5轮）
    if chat_history:
        recent_history = chat_history[-10:]  # 最近5轮对话
        messages.extend(recent_history)
    
    messages.append({"role": "user", "content": user_input})

    resp = llm_router.invoke(messages)
    chosen_npc = resp.content.strip()
    
    # 确保选择的NPC是有效的
    valid_npcs = ["村长", "铁匠", "药师"]
    if chosen_npc not in valid_npcs:
        chosen_npc = "村长"  # 默认选择
    
    return {"npc_targets": [chosen_npc]}
