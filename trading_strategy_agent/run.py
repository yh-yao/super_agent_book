import os
from agents.data_agent import load_prices, add_indicators
from agents.strategy_agent import search_ma_params
from agents.report_agent import plot_equity, make_report
def main():
    os.makedirs("reports", exist_ok=True)
    df = load_prices("data/sample_prices.csv")
    df = add_indicators(df)
    best = search_ma_params(df)
    eq = best["metrics"]["equity"]
    equity_png = "reports/equity.png"
    plot_equity(df, eq, equity_png)
    make_report(best, "reports/strategy_report.md", equity_png)
    print("Done. See reports/strategy_report.md")
if __name__ == "__main__":
    main()
