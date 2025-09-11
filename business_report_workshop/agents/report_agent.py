class ReportAgent:
    def run(self, strategy_text, chart_path):
        report = f"# 市场分析报告\n\n{strategy_text}\n\n"
        report += f"![趋势图]({chart_path})\n"
        with open("outputs/report.md", "w", encoding="utf-8") as f:
            f.write(report)
        return "outputs/report.md"
