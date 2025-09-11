from agents.memory_agent import MemoryAgent
from agents.dialogue_agent import DialogueAgent
from agents.planner_agent import PlannerAgent

class NPCChain:
    def __init__(self, background):
        self.memory = MemoryAgent()
        self.dialogue = DialogueAgent()
        self.planner = PlannerAgent()
        self.background = background

    def interact(self, player_input):
        self.memory.add_event(player_input)
        action = self.planner.next_action()
        response = self.dialogue.run(player_input, self.background, self.memory.recall())
        return {"npc_response": response, "npc_action": action}
