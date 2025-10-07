import os, ast, re
from .workspace import list_files

_COMPLEXITY_TOKENS = {"if", "for", "while", "and", "or", "try", "except", "with", "elif"}

def _py_complexity(src: str) -> int:
    count = 1
    for kw in _COMPLEXITY_TOKENS:
        count += len(re.findall(r"\b"+re.escape(kw)+r"\b", src))
    return count

def analyze_python_file(path: str) -> dict:
    info = {"path": path, "lang": "python", "functions": [], "classes": [], "todo": [],
            "has_print": False, "mutable_defaults": [], "complexity": 0, "imports": [], "content": ""}
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        info["content"] = src
    except Exception as e:
        info["error"] = f"读取错误: {e}"
        return info

    info["complexity"] = _py_complexity(src)
    info["has_print"] = "print(" in src

    for m in re.finditer(r"#\s*(TODO|FIXME|XXX)\b(.*)", src):
        info["todo"].append({"line": src.count('\n', 0, m.start())+1, "tag": m.group(1), "text": m.group(2).strip()})

    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        info["error"] = f"语法错误: 第{e.lineno}行 {e.msg}"
        return info

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                info["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            info["imports"].append(mod)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defaults = []
            if node.args.defaults:
                for arg, d in zip(node.args.args[-len(node.args.defaults):], node.args.defaults):
                    if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                        defaults.append({"arg": arg.arg, "type": type(d).__name__, "lineno": node.lineno})
            info["functions"].append({"name": node.name, "lineno": node.lineno, "defaults": defaults})
            for md in defaults:
                info["mutable_defaults"].append({"function": node.name, **md})
        elif isinstance(node, ast.ClassDef):
            info["classes"].append({"name": node.name, "lineno": node.lineno})

    return info

def analyze_js_like_file(path: str) -> dict:
    info = {"path": path, "lang": "js/ts", "functions": [], "classes": [], "todo": [], "has_console_log": False}
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
    except Exception as e:
        info["error"] = f"读取错误: {e}"
        return info
    info["has_console_log"] = "console.log(" in src
    for m in re.finditer(r"function\s+([A-Za-z_]\w*)\s*\(", src):
        info["functions"].append({"name": m.group(1), "lineno": src.count('\n', 0, m.start())+1})
    for m in re.finditer(r"class\s+([A-Za-z_]\w*)\b", src):
        info["classes"].append({"name": m.group(1), "lineno": src.count('\n', 0, m.start())+1})
    for m in re.finditer(r"//\s*(TODO|FIXME|XXX)\b(.*)", src):
        info["todo"].append({"line": src.count('\n', 0, m.start())+1, "tag": m.group(1), "text": m.group(2).strip()})
    return info

def analyze(root: str) -> dict:
    files = list_files(root)
    out = {"root": root, "files": [], "summary": {"python": 0, "js_ts": 0, "issues": 0}}
    for p in files:
        if p.endswith(".py"):
            info = analyze_python_file(p)
            out["files"].append(info)
            out["summary"]["python"] += 1
            if info.get("has_print") or info.get("mutable_defaults"):
                out["summary"]["issues"] += 1
        else:
            info = analyze_js_like_file(p)
            out["files"].append(info)
            out["summary"]["js_ts"] += 1
            if info.get("has_console_log"):
                out["summary"]["issues"] += 1
    return out

def render_markdown_report(analysis: dict, include_code: bool = False) -> str:
    lines = []
    lines.append("# 智能编程助手分析报告")
    lines.append(f"- 根目录: `{analysis.get('root')}`")
    s = analysis.get("summary", {})
    lines.append(f"- 文件: Python={s.get('python',0)}, JS/TS={s.get('js_ts',0)}, 潜在问题={s.get('issues',0)}")
    lines.append("")
    for f in analysis.get("files", []):
        lines.append(f"## {f.get('path')}")
        if f.get("error"):
            lines.append(f"- 错误: {f.get('error')}")
        else:
            if f.get("lang") == "python":
                lines.append(f"- 语言: Python, 复杂度: {f.get('complexity')}")
                if f.get("imports"):
                    lines.append(f"- 导入: {', '.join(f.get('imports'))}")
                if f.get("classes"):
                    lines.append(f"- 类: {', '.join([c['name'] for c in f.get('classes')])}")
                if f.get("functions"):
                    lines.append(f"- 函数: {', '.join([func['name'] for func in f.get('functions')])}")
                if f.get("todo"):
                    lines.append("- 待办事项:")
                    for todo in f.get("todo"):
                        lines.append(f"  - 第{todo['line']}行: {todo['tag']} - {todo['text']}")
            else:
                lines.append(f"- 语言: {f.get('lang')}")
                if f.get("has_console_log"):
                    lines.append("- 包含 console.log")

        if include_code and f.get('content'):
            lines.append("\n**文件内容:**\n")
            lines.append(f"```{f.get('lang')}\n{f.get('content')}\n```\n")
        
        lines.append("")
            
    return "\n".join(lines)
