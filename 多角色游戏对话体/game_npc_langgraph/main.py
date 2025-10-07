from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from .npc_agents import npc_node, npc_profiles
from .router import route_node

class GameState(TypedDict):
    input: str                    # 玩家输入
    npc_targets: List[str]       # 路由结果
    output: str                  # NPC输出
    chat_history: List[Dict[str, Any]]  # 聊天历史记录

def build_app():
    graph = StateGraph(GameState)

    # 路由节点
    graph.add_node("router", route_node)

    # 添加NPC节点
    for npc in npc_profiles:
        graph.add_node(npc, npc_node(npc))

    # 流程：router -> npc -> end
    graph.set_entry_point("router")

    # 添加条件边
    def route_to_npc(state):
        """根据路由结果决定去哪个NPC"""
        targets = state.get("npc_targets", [])
        if targets and targets[0] in npc_profiles:
            return targets[0]
        else:
            return "村长"  # 默认选择村长

    # 创建路由映射
    route_mapping = {npc: npc for npc in npc_profiles.keys()}

    graph.add_conditional_edges(
        "router",
        route_to_npc,
        route_mapping
    )

    for npc in npc_profiles:
        graph.add_edge(npc, END)

    return graph.compile()

def run_game():
    app = build_app()
    print("🎮 欢迎来到 NPC 村落！（输入 quit 退出）")
    print("📋 可用的NPC角色：")
    print("   🏛️ 村长 - 村庄管理、历史故事、一般建议")
    print("   ⚔️ 铁匠 - 武器装备、打造修理")
    print("   🌿 药师 - 草药治疗、健康咨询")
    print("💡 提示：直接说话，系统会自动为你选择合适的NPC回答")
    print("📚 注意：所有NPC都能看到完整的对话历史")
    print("-" * 50)
    
    # 初始化聊天历史
    chat_history = []
    
    while True:
        user_input = input("你: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 游戏结束，再见！")
            break
        
        # 构建包含历史记录的状态
        state = {
            "input": user_input,
            "chat_history": chat_history
        }
        
        result = app.invoke(state)
        npc_response = result["output"]
        print(npc_response)
        
        # 更新历史记录
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": npc_response})

if __name__ == "__main__":
    run_game()
