# SmartCoder Agent

**SmartCoder** is a fully autonomous AI agent that can understand and carry out complex coding tasks on your local codebase. It is powered by a Large Language Model (LLM) to analyze, plan, and execute changes to your code.

## Features

- **Autonomous Operation**: Simply provide an instruction, and SmartCoder will handle the rest.
- **Code Analysis**: Automatically analyzes your codebase to understand the context.
- **LLM-Powered Planning**: Generates a step-by-step plan to implement your request.
- **Self-Correction**: If a plan fails, SmartCoder will re-analyze the problem and attempt to correct its own plan.
- **Safe Dry-Runs**: All changes are tested in a dry-run mode before any files are modified on disk.

## Quick Start

### 1. Installation

Clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/your-repo/smartcoder-agent.git
cd smartcoder-agent
pip install -e .
```

### 2. Set up your OpenAI API Key

SmartCoder uses OpenAI's GPT models. You need to set your API key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Run the Agent

Use the `auto` command to give SmartCoder an instruction. You need to provide the path to your project and a clear instruction for the task you want to perform.

```bash
smartcoder auto -p /path/to/your/project -i "your instruction here"
```

For example, to refactor a function named `old_function` to `new_function` in a demo project, you would run:

```bash
smartcoder auto -p ./examples/demo_project -i "rename the function 'greeting' to 'say_hello'"
```

To apply the changes directly to your files, use the `--apply` flag:

```bash
smartcoder auto -p ./examples/demo_project -i "add a new function that says goodbye" --apply
```

## How It Works

The `auto` command orchestrates a sequence of steps:

1.  **Analyze**: It scans your project to build a contextual understanding of your code.
2.  **Plan**: It sends the analysis and your instruction to an LLM to generate a detailed execution plan.
3.  **Execute (Dry-Run)**: It performs a dry-run of the plan to verify the changes without modifying any files. If the plan fails, it will loop back to the planning step, providing the error as additional context to the LLM.
4.  **Apply (Optional)**: If the dry-run is successful and you've used the `--apply` flag, the agent will write the changes to your files.
5.  **Verify**: It performs a final syntax check on the modified files to ensure code integrity.

All logs for each run are saved in the `.smartcoder/logs` directory within your project.
