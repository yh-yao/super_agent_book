# Trading Agents Package (Teaching Demo)

本项目演示了一个教学用的交易代理系统，包含 **三种策略 Agent**：

- **Rule**: 纯规则策略，基于均线交叉生成 BUY / SELL 信号。
- **LLM**: 大模型策略，输入 RSI 和均线指标，让 LLM 决策 BUY / SELL / HOLD。
- **Hybrid**: 混合策略，结合规则、风险控制与 LLM 辅助，避免明显亏损并提升稳定性。

---

## 安装依赖

在项目根目录运行：

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_openai_api_key
```
---

## 运行方式

进入项目目录后，可以选择不同策略模式：

### Rule 策略
```bash
python streaming_main.py --mode rule --budget 100000 --short 5 --long 20
```

### LLM 策略
```bash
python streaming_main.py --mode llm --budget 100000 --short 5 --long 20
```

### Hybrid 策略（推荐）
```bash
python streaming_main.py --mode hybrid --budget 100000 --short 5 --long 20
```

---

## 参数说明
- `--mode`: 运行模式，可选 `rule` / `llm` / `hybrid`  
- `--budget`: 初始资金 (默认 100000)  
- `--short`: 短期均线窗口 (默认 5)  
- `--long`: 长期均线窗口 (默认 20)  

---

## 结果输出
运行后会：
- 打印每日价格、短期/长期均线、RSI 值  
- 输出决策说明（规则解释或 LLM 辅助信号）  
- 在结束时输出最终的投资组合报告，包括资金余额、持仓股数、组合总价值等  

---

## 文件结构
```
trading_agents_package_teaching/
├─ agents/
│  ├─ strategy_agent_rule.py      # 规则策略
│  ├─ strategy_agent_llm.py       # 大模型策略
│  ├─ strategy_agent_hybrid.py    # 混合策略
│  ├─ data_agent.py               # 数据加载
│  ├─ eval_agent.py               # 回测执行
│  ├─ report_agent.py             # 报告输出
├─ data/
│  └─ sample_prices.csv           # 示例价格数据
├─ streaming_main.py              # 主程序
├─ requirements.txt               # 依赖列表
└─ README.md                      # 项目说明
```

---

## 推荐使用方式
建议优先使用 **Hybrid 策略**：
- 在强信号时由规则直接决策（避免 LLM 出错）  
- 在模糊区间时引入 LLM 提供辅助意见  
- 内置止损/止盈逻辑，提高资金曲线稳定性  
