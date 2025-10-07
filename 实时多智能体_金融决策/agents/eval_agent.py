import pandas as pd

def eval_agent(data, mode, rule_agent=None, llm_agent=None, budget=100000, prev_state=None):
    dates = data["dates"]
    prices = data["prices"]
    state = prev_state or {"cash": budget, "shares": 0, "portfolio": budget, "history": []}

    today_price = prices[-1]
    action = "HOLD"

    if mode == "rule" and rule_agent:
        action = rule_agent(prices, state)
    elif mode == "llm" and llm_agent:
        action = llm_agent(prices, state)

    if action == "BUY" and state["cash"] >= today_price:
        shares_to_buy = int(state["cash"] // today_price)
        state["cash"] -= shares_to_buy * today_price
        state["shares"] += shares_to_buy
    elif action == "SELL" and state["shares"] > 0:
        state["cash"] += state["shares"] * today_price
        state["shares"] = 0

    state["portfolio"] = state["cash"] + state["shares"] * today_price
    state["history"].append({"date": dates[-1], "price": today_price, "cash": state["cash"],
                             "shares": state["shares"], "portfolio": state["portfolio"], "action": action})
    return state
