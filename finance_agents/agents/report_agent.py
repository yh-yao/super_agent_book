import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def report_agent(state, init_budget=100000, mode=None):
    df = pd.DataFrame(state["history"])
    returns = df["portfolio"].pct_change().dropna()
    cagr = (df["portfolio"].iloc[-1] / init_budget) ** (252/len(df)) - 1
    sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() != 0 else 0
    mdd = ((df["portfolio"].cummax() - df["portfolio"]) / df["portfolio"].cummax()).max()

    plt.figure(figsize=(10,5))
    plt.plot(df["date"], df["portfolio"], label="Portfolio Value", color="blue")
    plt.xticks(rotation=45)
    plt.title("Portfolio Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.tight_layout()
    curve_filename = f"portfolio_curve_{mode}.png" if mode else "portfolio_curve.png"
    plt.savefig(curve_filename)
    plt.close()

    log_cols = ["date", "price", "cash", "shares", "portfolio", "action"]
    signal_log = df[log_cols].copy()
    log_filename = f"signals_log_{mode}.csv" if mode else "signals_log.csv"
    signal_log.to_csv(log_filename, index=False, encoding="utf-8-sig")

    report = f"Final Portfolio: {df['portfolio'].iloc[-1]:.2f}\n"
    report += f"CAGR: {cagr:.2%}, Sharpe: {sharpe:.2f}, MDD: {mdd:.2%}\n"
    report += f"交易日志已保存到 {log_filename}"

    return {"report": report, "df": df}
