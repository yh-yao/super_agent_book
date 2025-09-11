import numpy as np
import pandas as pd
def crossover_signals(df: pd.DataFrame, fast: int, slow: int) -> pd.DataFrame:
    out = df.copy()
    out['fast'] = out['close'].rolling(fast).mean()
    out['slow'] = out['close'].rolling(slow).mean()
    out['signal'] = 0
    out.loc[out['fast'] > out['slow'], 'signal'] = 1
    out.loc[out['fast'] < out['slow'], 'signal'] = -1
    out['signal'] = out['signal'].shift(1).fillna(0)
    return out

def backtest(df: pd.DataFrame, signal_col='signal', fee=0.0005) -> dict:
    out = df.copy()
    sig = out[signal_col].fillna(0)
    ret = out['return'].fillna(0)
    strat_ret = sig * ret
    turns = sig.diff().abs().fillna(0)
    strat_ret_after = strat_ret - fee * turns
    equity = (1 + strat_ret_after).cumprod()
    ann = 252
    cagr = equity.iloc[-1] ** (ann / len(equity)) - 1 if len(equity)>0 else 0
    vol = np.std(strat_ret_after) * np.sqrt(ann)
    sharpe = (np.mean(strat_ret_after) * ann) / vol if vol > 0 else 0
    roll_max = equity.cummax()
    dd = equity / roll_max - 1
    mdd = dd.min()
    return {"cagr": float(cagr), "sharpe": float(sharpe), "mdd": float(mdd), "equity": equity, "strat_ret": strat_ret_after}
