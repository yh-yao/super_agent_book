import itertools
from .backtest import crossover_signals, backtest
def search_ma_params(df, fast_grid=(5,10,15), slow_grid=(20,30,50)):
    best = None
    best_res = None
    for f in fast_grid:
        for s in slow_grid:
            if f >= s: 
                continue
            sig_df = crossover_signals(df, f, s)
            res = backtest(sig_df)
            score = (res['sharpe'], res['cagr'])
            if best is None or score > best:
                best, best_res = score, (f, s, res)
    f, s, res = best_res
    return {"fast": f, "slow": s, "metrics": res}
