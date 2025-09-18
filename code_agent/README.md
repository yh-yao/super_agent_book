# SmartCoder Agent

SmartCoder Agent 是一个 **本地可运行的智能代码助手**。  
它能一步步完成 **分析 → 生成修改计划 → 应用修改 → 验证** 的流程。  
即使没有联网、没有 LLM（大语言模型），也能完成很多常见的代码改写任务。

适合 **学生和初学者** 使用，可以帮助理解代码、练习调试，也可以在学习编程规范时做自动修改。

---

## 🚀 快速开始（复制就能跑）

```bash
# 0) 建议使用虚拟环境
python3 -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

# 1) 解压并安装
unzip smartcoder-agent.zip
cd smartcoder-agent
pip install -e .

# 2) 自动执行（推荐）
# 预览修改
smartcoder auto -p ./examples/demo_project -i "add logging to all functions and replace print with logging"

# 应用修改
smartcoder auto -p ./examples/demo_project -i "add logging to all functions and replace print with logging" --apply

# 3) 分步执行（可选）
smartcoder analyze ./examples/demo_project
smartcoder plan -p ./examples/demo_project -i "add logging & replace print"
smartcoder edit -p ./examples/demo_project -i "add logging & replace print" --apply
smartcoder verify -p ./examples/demo_project

# 4) 超短演示（直接分析代码片段）
smartcoder analyze --code "def f(x=[]): print(x); return 1"
```

> 提示：`edit` 默认是 **dry-run**（只看 diff），加上 `--apply` 才会写回文件。

---

## 功能特点

- **支持输入多种形式的代码**
  - 代码片段（直接一行代码）
  - 单个 `.py` 文件
  - 整个目录
  - 压缩包（zip 会自动解压到临时目录）

- **分析能力（Analyze）**
  - Python：函数、类、复杂度评分、是否使用 `print`、是否有可变默认参数（常见坑）、`TODO` 注释
  - JS/TS：函数、类、`console.log`、`TODO` 注释（启发式）

- **修改能力（Edit）**
  - 给函数入口自动加 `logging.info(...)`
  - 将 `print(...)` 改成 `logging.info(...)`
  - 安全重命名函数/变量
  - 修复可变默认参数（`[] / {}` → `None` 并在函数里加守卫）

- **验证能力（Verify）**
  - 对所有 `.py` 文件执行语法检查
  - 报告每个文件是否正常

- **日志留痕**
  - 每次操作都会生成 Markdown 日志，包含步骤和 diff
  - 日志保存在 `.smartcoder/logs/`

---

## 安装与运行（详细）

### 1. 创建虚拟环境（推荐）
```bash
python3 -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. 安装 SmartCoder Agent
```bash
unzip smartcoder-agent.zip
cd smartcoder-agent
pip install -e .
```

### 3. 验证安装
```bash
smartcoder --help
```

---

## 常见用法（Cheatsheet）

### A. 分析（Analyze）

1. **分析代码片段**
   ```bash
   smartcoder analyze --code "def f(x=[]): print(x); return 1"
   ```
   👉 检查代码里是否有 `print` 和可变默认参数。

2. **分析单个文件**
   ```bash
   smartcoder analyze your_script.py
   ```
   👉 输出函数、类、复杂度、潜在问题。

3. **分析整个目录**
   ```bash
   smartcoder analyze ./my_project
   ```
   👉 扫描目录下所有 `.py`、`.js`、`.ts` 文件。

---

### B. 生成修改计划（Plan）

```bash
smartcoder plan -p your_script.py -i "replace print with logging"
```

👉 输出一份“修改计划”，告诉你会执行哪些步骤（例如：替换 print → logging）。

---

### C. 应用修改（Edit）

有两种方式：

#### 1. **自然语言指令（-i）**
```bash
# 只预览（dry-run，显示 diff，不会写回文件）
smartcoder edit -p your_script.py -i "replace print with logging"

# 真正修改（--apply 会写回文件）
smartcoder edit -p your_script.py -i "replace print with logging" --apply
```

#### 2. **显式 flags（更精确，不用 -i）**
```bash
# 给函数入口加 logging，并替换 print
smartcoder edit -p your_script.py --add-logging --replace-print

# 应用修改
smartcoder edit -p your_script.py --add-logging --replace-print --apply
```

#### 其他操作
- **重命名函数/变量**
  ```bash
  smartcoder edit -p your_script.py --rename-func old_name new_name --apply
  ```

- **修复可变默认参数**
  ```bash
  smartcoder edit -p your_script.py --fix-mutable-defaults --apply
  ```

---

### D. 验证（Verify）

```bash
smartcoder verify -p your_script.py
```

👉 检查 Python 文件是否能正常编译。

---

### E. 自动模式（Auto）

这是最推荐的用法，一条指令完成所有操作。

```bash
# 预览所有步骤和最终的 diff
smartcoder auto -p ./my_project -i "your instruction here"

# 应用修改
smartcoder auto -p ./my_project -i "your instruction here" --apply
```

👉 工具会自动完成 `analyze` -> `plan` -> `edit` -> `verify` 的完整流程。

---

## 使用建议

- 默认是 **dry-run**，先看 diff，再决定要不要 `--apply`。
- 修改和日志都会保存，你随时可以回滚。
- 没有 `TODO` 注释也没关系，工具依然能分析和修改。
- JS/TS 目前只有分析功能；Java 暂时不支持修改（未来可扩展）。

---

## 学习提示

- **为什么要替换 `print`？**  
  在实际项目中，推荐用 `logging` 代替 `print`，因为 `logging` 可以设置等级、保存到文件，更适合生产环境。

- **为什么可变默认参数是坑？**  
  Python 中函数的默认参数只会在定义时计算一次，如果是 `[]` 或 `{}`，会被多个调用共享，可能导致意想不到的 bug。  
  改为 `None` 并在函数里初始化是更安全的写法。

- **为什么先 dry-run？**  
  直接改代码可能有风险，先看 diff（改动内容），确认没问题再 `--apply`，这是安全编程习惯。

---

## 日志与报告

- `analysis_report.md`：分析结果
- `.smartcoder/logs/edit-*.md`：每次编辑操作的日志，包含计划与 diff
- 修改后的源文件：只有加了 `--apply` 才会真的写回

---

## 可选：接入 LLM

- 默认情况下，修改计划由 **规则引擎** 生成（关键词触发）。
- 如果设置了 `OPENAI_API_KEY` 环境变量，则会自动调用 LLM 生成更智能的修改计划。（不影响基础功能，也不需要修改命令）。
- 配置你的API KEY来使用LLM：export OPENAI_API_KEY='your_api_key_here'

---

## 总结

- 想快速检查：用 `analyze`  
- 想看看会怎么改：用 `plan` 或 `edit`（不加 `--apply`）  
- 想真正改：`edit --apply`  
- 想确认改后能跑：`verify`  

---

Happy Coding! 🎉
