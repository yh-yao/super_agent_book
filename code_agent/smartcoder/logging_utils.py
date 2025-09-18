import os, time, pathlib

def ensure_log_dir(root: str) -> str:
    log_dir = os.path.join(root, ".smartcoder", "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def new_log_path(root: str, prefix: str = "run") -> str:
    log_dir = ensure_log_dir(root)
    ts = time.strftime("%Y%m%d-%H%M%S")
    return os.path.join(log_dir, f"{prefix}-{ts}.md")

def write_log(path: str, content: str) -> None:
    base = pathlib.Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content if content.endswith("\n") else content + "\n")
