import os
from .diff_utils import unified_diff_text

def _read(path: str) -> str:
    """Read file content."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _write(path: str, s: str) -> None:
    """Write content to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

def apply_actions(root: str, files: list[str], actions: list[dict], dry_run: bool = True) -> str:
    """Apply code changes from LLM suggestions."""
    log = []
    
    for i, act in enumerate(actions, 1):
        action = act.get("action")
        log.append(f"## Step {i}: {action}")
        log.append(f"- Explain: {act.get('explain', '')}")

        if action == "noop":
            log.append("- Nothing to do.")
            continue

        if action != "edit":
            log.append(f"- Unsupported action: {action}")
            continue

        args = act.get("args", {})
        fpath = os.path.join(root, args.get("file", ""))
        if not os.path.exists(fpath):
            log.append(f"- Error: File not found: {fpath}")
            continue

        try:
            original = _read(fpath)
            old_code = args.get("old", "")
            new_code = args.get("new", "")

            if old_code:
                if old_code not in original:
                    log.append(f"- Error: Could not find code to replace in {fpath}")
                    continue
                updated = original.replace(old_code, new_code)
            else:
                # For adding new code, add with spacing
                updated = original.rstrip() + "\n\n" + new_code + "\n"

            diff = unified_diff_text(original, updated, fromfile=fpath, tofile=fpath)
            if not dry_run:
                _write(fpath, updated)
            log.append(f"**Patch** `{fpath}`:\n\n```diff\n{diff}\n```")

        except Exception as e:
            log.append(f"- Error: Failed to apply change: {str(e)}")

        log.append("")

    return "\n".join(log)
