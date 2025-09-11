import pandas as pd
from pathlib import Path

def load_prices(csv_path: str = "data/sample_prices.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df['return'] = df['close'].pct_change()
    return df

def add_indicators(df: pd.DataFrame, windows=(5, 10, 20, 50)) -> pd.DataFrame:
    out = df.copy()
    for w in windows:
        out[f"ma_{w}"] = out['close'].rolling(w).mean()
    return out
