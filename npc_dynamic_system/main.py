from workflows.npc_chain import NPCChain

if __name__ == "__main__":
    npc = NPCChain(background="一位友善的村民，喜欢帮助玩家完成采矿任务。")
    npc.planner.add_goal("引导玩家前往矿洞")
    npc.planner.add_goal("协助玩家制作工具")

    result = npc.interact("你好，我需要一些帮助。")
    print("💬 NPC 对话:", result["npc_response"])
    print("🎯 NPC 行为:", result["npc_action"])
