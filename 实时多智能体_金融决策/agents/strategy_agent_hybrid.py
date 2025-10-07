import numpy as np
from openai import OpenAI
from agents.strategy_agent_llm import compute_rsi

client = OpenAI()

def strategy_agent_hybrid(prices, state, short=5, long=20):
    """混合策略：规则优先 + LLM 辅助"""
    rsi = compute_rsi(prices)
    short_ma = np.mean(prices[-short:]) if len(prices) >= short else None
    long_ma = np.mean(prices[-long:]) if len(prices) >= long else None

    # ===== 硬规则：强信号直接执行 =====
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

    # ===== 风险控制 =====
    if state["shares"] > 0:
        avg_cost = state.get("avg_cost", prices[-1])
        if prices[-1] < avg_cost * 0.95:  # 止损 5%
            return "SELL"
        if prices[-1] > avg_cost * 1.10:  # 止盈 10%
            return "SELL"

    # ===== 模糊区间，交给 LLM =====
    lookback = 7
    recent_prices = prices[-lookback:]
    recent_str = ", ".join([f"{p:.2f}" for p in recent_prices])

    short_ma_str = f"{short_ma:.2f}" if short_ma is not None else "None"
    long_ma_str = f"{long_ma:.2f}" if long_ma is not None else "None"
    rsi_str = f"{rsi:.2f}" if rsi is not None else "None"

    prompt = f"""
你是一个交易策略助手。请基于以下信息严格输出 BUY / SELL / HOLD：

- 最近{lookback}天价格: {recent_str}
- 当前价格: {prices[-1]}
- 短期均线({short}日): {short_ma_str}
- 长期均线({long}日): {long_ma_str}
- RSI(14): {rsi_str}
- 当前持仓股数: {state.get("shares",0)}

规则：
- RSI < 30 且未持仓: BUY
- RSI > 70 且已持仓: SELL
- 短均线上穿长均线: BUY
- 短均线下穿长均线: SELL
- 持仓亏损 >5%: SELL
- 持仓盈利 >10%: SELL
- 其余情况: HOLD

只输出一个词：BUY / SELL / HOLD
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "你是一个交易助手。"},
                      {"role": "user", "content": prompt}],
            temperature=0.0
        )
        decision = response.choices[0].message.content.strip().upper()
        if decision not in ["BUY", "SELL", "HOLD"]:
            decision = "HOLD"
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        decision = "HOLD"

    # ===== 更新平均成本（买入时） =====
    if decision == "BUY":
        state["avg_cost"] = prices[-1]

    return decision
