from agents.data_agent import DataAgent
from agents.strategy_agent import StrategyAgent
from agents.report_agent import ReportAgent

class BIChain:
    def __init__(self):
        self.data = DataAgent()
        self.strategy = StrategyAgent()
        self.report = ReportAgent()

    def run(self, csv_path):
        df, chart = self.data.run(csv_path)
        strategy_text = self.strategy.run(df.describe().to_string())
        report_path = self.report.run(strategy_text, chart)
        return report_path
