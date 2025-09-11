import os, matplotlib.pyplot as plt
from datetime import datetime
def plot_equity(df, equity, out_png):
    plt.figure(figsize=(9,4))
    plt.plot(df['date'], equity)
    plt.title('Strategy Equity Curve')
    plt.xlabel('Date'); plt.ylabel('Equity')
    plt.tight_layout(); plt.savefig(out_png, dpi=150); plt.close()
def make_report(params: dict, out_md: str, equity_png: str):
    fast, slow = params['fast'], params['slow']
    met = params['metrics']
    lines = [
      f"# Strategy Report ({datetime.now().strftime('%Y-%m-%d')})","",
      f"**Selected Strategy**: MA Crossover (fast={fast}, slow={slow})","",
      "## Key Metrics",
      f"- CAGR: {met['cagr']:.2%}",f"- Sharpe: {met['sharpe']:.2f}",f"- Max Drawdown: {met['mdd']:.2%}","",
      "## Equity Curve",f"![equity]({os.path.basename(equity_png)})",""
    ]
    with open(out_md, "w", encoding="utf-8") as f: f.write("\n".join(lines))
