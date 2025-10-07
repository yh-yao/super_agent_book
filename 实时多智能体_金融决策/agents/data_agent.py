import pandas as pd
import os

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_prices.csv")
    df = pd.read_csv(file_path)
    return df

def data_agent_stream(df, i):
    """返回第 i 天（含历史）的数据，模拟逐步加载"""
    sub_df = df.iloc[:i+1]
    return {"dates": sub_df["date"].tolist(), "prices": sub_df["price"].tolist()}
