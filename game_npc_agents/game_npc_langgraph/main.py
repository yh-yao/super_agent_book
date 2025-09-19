from langgraph.graph import StateGraph, END
from .npc_agents import npc_node, npc_profiles
from .router import route_node

def build_app():
    # 定义状态
    state_schema = {
        "input": str,         # 玩家输入
        "npc_targets": list,  # 路由结果
        "output": str         # NPC输出
    }

    graph = StateGraph(state_schema)

    # 路由节点
    graph.add_node("router", route_node)

    # 添加NPC节点
    for npc in npc_profiles:
        graph.add_node(npc, npc_node(npc))

    # 流程：router -> npc -> end
    graph.set_entry_point("router")

    for npc in npc_profiles:
        graph.add_edge("router", npc, condition=lambda s, n=npc: n in s["npc_targets"])
        graph.add_edge(npc, END)

    return graph.compile()

def run_game():
    app = build_app()
    print("🎮 欢迎来到 NPC 村落！（输入 quit 退出）")
    while True:
        user_input = input("你: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 游戏结束，再见！")
            break
        result = app.invoke({"input": user_input})
        print(result["output"])
