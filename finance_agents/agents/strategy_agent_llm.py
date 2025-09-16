import numpy as np
from openai import OpenAI

client = OpenAI()

def compute_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = np.diff(prices)
    gains = deltas[deltas > 0].sum() / period
    losses = -deltas[deltas < 0].sum() / period
    if losses == 0:
        return 100
    rs = gains / losses
    return 100 - (100 / (1 + rs))

def strategy_agent_llm(prices, state, short=5, long=20):
    """改进版 LLM 策略：硬约束 + 历史上下文"""
    rsi = compute_rsi(prices)
    short_ma = np.mean(prices[-short:]) if len(prices) >= short else None
    long_ma = np.mean(prices[-long:]) if len(prices) >= long else None

    # ===== 硬约束逻辑 =====
    if rsi is not None:
        if rsi < 25 and state["shares"] == 0:
            return "BUY"
        if rsi > 75 and state["shares"] > 0:
            return "SELL"

    if short_ma and long_ma:
        if short_ma > long_ma * 1.01:  # 金叉
            return "BUY"
        if short_ma < long_ma * 0.99:  # 死叉
            return "SELL"

    # ===== 历史上下文 =====
    lookback = 5
    recent_prices = prices[-lookback:]
    recent_str = ", ".join([f"{p:.2f}" for p in recent_prices])

    short_ma_str = f"{short_ma:.2f}" if short_ma is not None else "None"
    long_ma_str = f"{long_ma:.2f}" if long_ma is not None else "None"
    rsi_str = f"{rsi:.2f}" if rsi is not None else "None"

    prompt = f"""
你是一个交易教学助手。基于以下信息严格输出 BUY / SELL / HOLD：

- 最近{lookback}天价格: {recent_str}
- 当前价格: {prices[-1]}
- 短期均线({short}日): {short_ma_str}
- 长期均线({long}日): {long_ma_str}
- RSI(14): {rsi_str}
- 当前持仓股数: {state.get("shares",0)}

规则提示：
- 如果 RSI < 30 且未持仓，可以考虑 BUY
- 如果 RSI > 70 且已持仓，可以考虑 SELL
- 如果短均线上穿长均线，可以考虑 BUY
- 如果短均线下穿长均线，可以考虑 SELL
- 其他情况 HOLD

只输出一个词：BUY / SELL / HOLD
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "你是一个交易策略助手。"},
                      {"role": "user", "content": prompt}],
            temperature=0.0
        )
        decision = response.choices[0].message.content.strip().upper()
        if decision not in ["BUY", "SELL", "HOLD"]:
            decision = "HOLD"
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        decision = "HOLD"

    return decision
