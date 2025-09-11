import pandas as pd
import matplotlib.pyplot as plt

class ToolAgent:
    def fetch_financials(self, company, quarter):
        print(f"📊 获取 {company} {quarter} 财报数据")
        # 模拟数据
        data = pd.DataFrame({
            "指标": ["营收", "净利润", "毛利率"],
            "数值": [249.3, 27.1, "25%"]
        })
        return data

    def plot_trend(self, data):
        print("📈 绘制趋势图")
        plt.figure()
        plt.bar(data["指标"], [249.3, 27.1, 25])
        plt.ylabel("数值")
        plt.title("特斯拉 Q2 财报关键指标")
        path = "outputs/tesla_q2.png"
        plt.savefig(path)
        return path
