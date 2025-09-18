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
            "has_print": False, "mutable_defaults": [], "complexity": 0, "imports": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
    except Exception as e:
        info["error"] = f"read_error: {e}"
        return info

    info["complexity"] = _py_complexity(src)
    info["has_print"] = "print(" in src

    for m in re.finditer(r"#\s*(TODO|FIXME|XXX)\b(.*)", src):
        info["todo"].append({"line": src.count('\n', 0, m.start())+1, "tag": m.group(1), "text": m.group(2).strip()})

    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        info["error"] = f"syntax_error: line {e.lineno} {e.msg}"
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
        info["error"] = f"read_error: {e}"
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

def render_markdown_report(analysis: dict) -> str:
    lines = []
    lines.append("# SmartCoder Analysis Report")
    lines.append(f"- Root: `{analysis.get('root')}`")
    s = analysis.get("summary", {})
    lines.append(f"- Files: Python={s.get('python',0)}, JS/TS={s.get('js_ts',0)}, Potential issues={s.get('issues',0)}")
    lines.append("")
    for f in analysis.get("files", []):
        lines.append(f"## {f.get('path')}")
        if f.get("lang") == "python":
            lines.append("- Language: Python")
            if "error" in f:
                lines.append(f"- Error: `{f['error']}`")
                lines.append("")
                continue
            lines.append(f"- Functions: {', '.join([fn['name'] for fn in f.get('functions',[])]) or '(none)'}")
            lines.append(f"- Classes: {', '.join([cl['name'] for cl in f.get('classes',[])]) or '(none)'}")
            lines.append(f"- Complexity score (rough): {f.get('complexity')}")
            if f.get("has_print"):
                lines.append("- Uses print(): **yes**")
            if f.get("mutable_defaults"):
                md = '; '.join([f"{m['function']}:{m['arg']} ({m['type']})@{m['lineno']}" for m in f['mutable_defaults']])
                lines.append(f"- Mutable defaults: {md}")
            if f.get("todo"):
                lines.append("- TODOs:")
                for t in f["todo"]:
                    lines.append(f"  - L{t['line']} [{t['tag']}] {t['text']}")
        else:
            lines.append("- Language: JS/TS-like")
            if f.get("has_console_log"):
                lines.append("- Uses console.log(): **yes**")
            lines.append(f"- Functions: {', '.join([fn['name'] for fn in f.get('functions',[])]) or '(none)'}")
            lines.append(f"- Classes: {', '.join([cl['name'] for cl in f.get('classes',[])]) or '(none)'}")
            if f.get("todo"):
                lines.append("- TODOs:")
                for t in f["todo"]:
                    lines.append(f"  - L{t['line']} [{t['tag']}] {t['text']}")
        lines.append("")
    return "\n".join(lines)
