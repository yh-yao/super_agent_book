class PlannerAgent:
    def __init__(self):
        self.goals = []

    def add_goal(self, goal):
        self.goals.append(goal)

    def next_action(self):
        if self.goals:
            return f"执行任务: {self.goals.pop(0)}"
        return "等待玩家互动"
