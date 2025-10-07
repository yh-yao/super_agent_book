import numpy as np

def strategy_agent_rule(prices, state, short=5, long=20):
    if len(prices) < long:
        return "HOLD"
    short_ma = np.mean(prices[-short:])
    long_ma = np.mean(prices[-long:])
    if short_ma > long_ma and state.get("shares", 0) == 0:
        return "BUY"
    elif short_ma < long_ma and state.get("shares", 0) > 0:
        return "SELL"
    else:
        return "HOLD"
