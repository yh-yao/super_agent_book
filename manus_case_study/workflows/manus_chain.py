from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.tool_agent import ToolAgent

class ManusChain:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.tool = ToolAgent()

    def run(self, task):
        plan = self.planner.run(task)
        for step in plan["steps"]:
            self.executor.run(step)
        data = self.tool.fetch_financials("Tesla", "Q2")
        chart = self.tool.plot_trend(data)
        report = f"# 特斯拉 Q2 财报分析\n\n{data}\n\n趋势图见 {chart}"
        with open("outputs/report.md", "w", encoding="utf-8") as f:
            f.write(report)
        return report
