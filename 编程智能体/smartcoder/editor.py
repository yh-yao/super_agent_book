import os
from .diff_utils import unified_diff_text

def _read(path: str) -> str:
    """读取文件内容。"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _write(path: str, s: str) -> None:
    """将内容写入文件。"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

def apply_actions(root: str, files: list[str], actions: list[dict], dry_run: bool = True) -> str:
    """应用来自LLM建议的代码更改。"""
    log = []
    
    for i, act in enumerate(actions, 1):
        action = act.get("action")
        log.append(f"## 步骤 {i}: {action}")
        log.append(f"- 说明: {act.get('explain', '')}")

        if action == "noop":
            log.append("- 无需操作。")
            continue

        if action != "edit":
            log.append(f"- 不支持的操作: {action}")
            continue

        args = act.get("args", {})
        fpath = os.path.join(root, args.get("file", ""))
        if not os.path.exists(fpath):
            log.append(f"- 错误: 文件未找到: {fpath}")
            continue

        try:
            original = _read(fpath)
            old_code = args.get("old", "")
            new_code = args.get("new", "")

            if old_code:
                if old_code not in original:
                    log.append(f"- 错误: 在 {fpath} 中找不到要替换的代码")
                    continue
                updated = original.replace(old_code, new_code)
            else:
                # 添加新代码时，添加间距
                updated = original.rstrip() + "\n\n" + new_code + "\n"

            diff = unified_diff_text(original, updated, fromfile=fpath, tofile=fpath)
            if not dry_run:
                _write(fpath, updated)
            log.append(f"**补丁** `{fpath}`:\n\n```diff\n{diff}\n```")

        except Exception as e:
            log.append(f"- 错误: 应用更改失败: {str(e)}")

        log.append("")

    return "\n".join(log)
