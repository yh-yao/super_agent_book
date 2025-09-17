# 自进化商业报告生成代理 (集成谷歌搜索 + OpenAI)

一个完整的**自进化商业报告生成代理**项目，具备以下能力：
- 对自己生成的草稿进行反思
- **通过函数调用集成谷歌搜索**，获取缺失信息
- 迭代修订直到达到目标质量分数
- 智能搜索策略优化
- 实时过程输出和详细评分反馈

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥
```bash
# 设置 OpenAI API 密钥
export OPENAI_API_KEY="sk-..."

# 设置谷歌搜索 API 密钥
export GOOGLE_API_KEY="..."
export GOOGLE_CSE_ID="..."
```

### 3. 运行示例
```bash
# 基础运行 - 生成关于特定主题的商业报告
python main.py --prompt "研究谷歌最近的情况"

# 自定义参数运行
python main.py --prompt "分析苹果公司的市场策略" --steps 5 --target-words 1000 --target-score 0.85

# 查看帮助
python main.py --help
```

## 📊 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--prompt` | string | 必需 | 报告主题或用户需求 |
| `--steps` | int | 5 | 最大迭代步数 |
| `--target-words` | int | 800 | 目标字数 |
| `--target-score` | float | 0.86 | 目标质量分数 |
| `--out` | string | out.json | 输出文件路径 |

## 🔧 工作原理

### 1. 智能反思决策
每次迭代中，AI 会分析当前状况并决定：
- **搜索**：获取更多相关信息
- **修订**：改进当前草稿内容

### 2. 自适应搜索策略
AI 会根据上下文自动优化搜索查询：
```
步骤 1: "latest news Google 2025"
步骤 2: "Google latest news September 2025"  
步骤 3: "Google news September 2025"
```

### 3. 多维度质量评估
- **相关性** (30%)：与用户需求的匹配度
- **完整性** (25%)：报告结构的完整性
- **冗余度** (20%)：内容重复程度
- **长度匹配** (15%)：与目标字数的契合度
- **结构** (10%)：格式和组织结构

### 4. 实时进度反馈
```
🚀 开始自进化报告生成流程，目标：3步，800字
============================================================

📍 步骤 1/3
----------------------------------------
🤔 正在反思决策...
🔍 决定搜索：Google latest news 2025
📊 找到 5 个搜索结果
✍️  基于搜索结果重新生成报告...
📊 评估报告质量...
📈 当前得分: 0.754 (目标: 0.86)
   - 相关性: 0.975
   - 完整性: 1.000
   - 长度匹配: 0.953
   - 结构: 1.000
   - 冗余度: 1.000
```

## 📁 输出文件

运行完成后，会生成包含以下信息的 JSON 文件：

```json
{
  "summary": "生成的商业报告内容",
  "best_score": {
    "relevance": 0.975,
    "completeness": 1.0,
    "length_fit": 0.953,
    "structure": 1.0,
    "redundancy": 1.0,
    "total": 0.854
  },
  "search_summary": [
    {
      "step": 1,
      "query": "Google latest news 2025",
      "results": [搜索结果详情]
    }
  ],
  "history": [详细的执行历史],
  "learned_params": {
    "bullet_prob": 0.55,
    "target_words": 800
  }
}
```

## 🌟 特性

- ✅ **完全自动化**：无需人工干预的报告生成
- ✅ **智能搜索**：根据需要自动搜索最新信息
- ✅ **质量驱动**：基于多维度评分的迭代优化
- ✅ **实时反馈**：详细的过程输出和进度跟踪
- ✅ **中文优化**：针对中文内容的字数统计和评分
- ✅ **灵活配置**：可调节的目标参数和输出格式

## 🛠️ 技术栈

- **LLM**: OpenAI GPT-4
- **搜索**: Google Custom Search API
- **语言**: Python 3.8+
- **主要依赖**: openai, requests, argparse

## 📝 使用示例

### 生成科技公司分析报告
```bash
python main.py --prompt "分析特斯拉2025年的发展战略和市场表现" --target-words 1200
```

### 生成市场趋势报告
```bash
python main.py --prompt "分析人工智能在医疗行业的应用趋势" --steps 3 --target-score 0.9
```

### 生成竞争分析报告
```bash
python main.py --prompt "比较苹果和三星在智能手机市场的竞争策略" --target-words 1500
```
