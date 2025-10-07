import os, shutil, tempfile, zipfile

def load_input_to_workspace(target: str | None, code_snippet: str | None = None) -> str:
    """
    将输入规范化为工作空间目录。
    返回工作空间根目录的绝对路径。
    """
    if code_snippet is not None:
        root = tempfile.mkdtemp(prefix="smartcoder_snippet_")
        with open(os.path.join(root, "snippet.py"), "w", encoding="utf-8") as f:
            f.write(code_snippet)
        return root

    if target is None:
        raise ValueError("请提供路径或使用 --code 参数。")

    target = os.path.abspath(target)
    if not os.path.exists(target):
        raise FileNotFoundError(f"输入路径未找到: {target}")

    if zipfile.is_zipfile(target):
        root = tempfile.mkdtemp(prefix="smartcoder_zip_")
        with zipfile.ZipFile(target, "r") as zf:
            zf.extractall(root)
        return root

    if os.path.isfile(target):
        root = tempfile.mkdtemp(prefix="smartcoder_file_")
        shutil.copy2(target, os.path.join(root, os.path.basename(target)))
        return root

    return target  # 目录

def list_files(root: str, exts: tuple[str,...] = (".py", ".js", ".ts", ".tsx")) -> list[str]:
    results = []
    for base, _, files in os.walk(root):
        parts = set(base.replace("\\", "/").split("/"))
        if ".git" in parts or ".smartcoder" in parts or "__pycache__" in parts:
            continue
        for fn in files:
            if fn.startswith("."):
                continue
            p = os.path.join(base, fn)
            if p.endswith(exts):
                results.append(p)
    return results
