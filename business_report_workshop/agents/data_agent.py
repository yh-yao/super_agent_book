import pandas as pd
import matplotlib.pyplot as plt

class DataAgent:
    def run(self, csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna()  # 缺失值清洗
        df.describe().to_csv("outputs/summary.csv")

        # 简单可视化
        plt.figure()
        df.plot(x="Month", y="Sales", kind="line")
        plt.savefig("outputs/sales_trend.png")
        return df, "outputs/sales_trend.png"
