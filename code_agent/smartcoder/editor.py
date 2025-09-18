import os, ast, io, re, tokenize
from .workspace import list_files
from .diff_utils import unified_diff_text

def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _write(path: str, s: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

def _ensure_import_logging_text(src: str) -> tuple[str, bool]:
    if re.search(r"^\s*import\s+logging\b", src, re.M):
        return src, False
    lines = src.splitlines(keepends=True)
    insert_idx = 0
    if lines and lines[0].lstrip().startswith('"""'):
        for i, line in enumerate(lines[1:], 1):
            if '"""' in line:
                insert_idx = i + 1
                break
    lines.insert(insert_idx, "import logging\n")
    return "".join(lines), True

def add_logging_to_functions_text(py_path: str) -> tuple[bool, str, str]:
    original = _read(py_path)
    src, did_import = _ensure_import_logging_text(original)
    try:
        tree = ast.parse(src, filename=py_path)
    except SyntaxError:
        return False, original, ""

    lines = src.splitlines(keepends=True)
    changed_any = did_import
    offset = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body = node.body or []
            insert_line = node.lineno
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
                insert_line = body[0].end_lineno or (body[0].lineno + 1)
            indent = " " * ((body[0].col_offset if body else node.col_offset + 4))
            log_line = f"{indent}logging.info('Entering {node.name}')\n"
            idx = insert_line + offset
            lines.insert(idx, log_line)
            offset += 1
            changed_any = True

    updated = "".join(lines)
    if not changed_any:
        return False, original, ""
    diff = unified_diff_text(original, updated, fromfile=py_path, tofile=py_path)
    return True, updated, diff

def replace_print_with_logging_text(py_path: str) -> tuple[bool, str, str]:
    original = _read(py_path)
    src, did_import = _ensure_import_logging_text(original)
    changed = False
    out = []
    g = tokenize.generate_tokens(io.StringIO(src).readline)
    for tok in g:
        ttype, tstring, start, end, line = tok
        if ttype == tokenize.NAME and tstring == "print":
            out.append((ttype, "logging.info", start, end, line))
            changed = True
        else:
            out.append(tok)
    updated = tokenize.untokenize(out)
    if not (changed or did_import):
        return False, original, ""
    diff = unified_diff_text(original, updated, fromfile=py_path, tofile=py_path)
    return True, updated, diff

def rename_identifier_text(py_path: str, old: str, new: str) -> tuple[bool, str, str]:
    original = _read(py_path)
    changed = False
    out = []
    g = tokenize.generate_tokens(io.StringIO(original).readline)
    for tok in g:
        ttype, tstring, start, end, line = tok
        if ttype == tokenize.NAME and tstring == old:
            out.append((ttype, new, start, end, line))
            changed = True
        else:
            out.append(tok)
    updated = tokenize.untokenize(out)
    if not changed:
        return False, original, ""
    diff = unified_diff_text(original, updated, fromfile=py_path, tofile=py_path)
    return True, updated, diff

def fix_mutable_defaults_text(py_path: str) -> tuple[bool, str, str]:
    original = _read(py_path)
    try:
        tree = ast.parse(original, filename=py_path)
    except SyntaxError:
        return False, original, ""

    lines = original.splitlines(keepends=True)
    updated_text = original
    changed_any = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.args.defaults:
            items = []
            for arg, d in zip(node.args.args[-len(node.args.defaults):], node.args.defaults):
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    items.append((arg.arg, type(d).__name__))
            if not items:
                continue

            start = node.lineno - 1
            end_line = node.body[0].lineno - 1 if node.body else node.lineno
            sig_block = "".join(lines[start:end_line])
            new_sig = sig_block
            for (arg_name, def_type) in items:
                new_sig = re.sub(rf"(\b{re.escape(arg_name)}\s*=\s*)(\[\s*\]|\{{\s*\}})", r"\1None", new_sig)
            if new_sig != sig_block:
                updated_text = updated_text.replace(sig_block, new_sig, 1)
                changed_any = True

            insert_after = node.lineno
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(getattr(node.body[0], "value", None), ast.Constant) and isinstance(node.body[0].value.value, str):
                insert_after = (node.body[0].end_lineno or node.body[0].lineno)

            indent = " " * (node.col_offset + 4)
            guard_lines = []
            for (arg_name, def_type) in items:
                default_value = "[]" if def_type == "List" else "{}"
                guard_lines.append(f"{indent}if {arg_name} is None:\n")
                guard_lines.append(f"{indent}    {arg_name} = {default_value}\n")

            ulines = updated_text.splitlines(keepends=True)
            ulines.insert(insert_after, "".join(guard_lines))
            updated_text = "".join(ulines)

    if not changed_any:
        return False, original, ""
    diff = unified_diff_text(original, updated_text, fromfile=py_path, tofile=py_path)
    return True, updated_text, diff

def apply_actions(root: str, files: list[str], actions: list[dict], dry_run: bool = True) -> str:
    log = []
    py_targets = [f for f in files if f.endswith(".py")]
    for i, act in enumerate(actions, 1):
        a = act.get("action")
        log.append(f"## Step {i}: {a}")
        log.append(f"- Explain: {act.get('explain', '')}")
        args = act.get("args", {})

        if a == "rename_function":
            old, new = args.get("old"), args.get("new")
            if not old or not new:
                log.append("- Skipped: missing old/new")
            else:
                for fpath in py_targets:
                    changed, updated, diff = rename_identifier_text(fpath, old, new)
                    if changed:
                        if not dry_run:
                            _write(fpath, updated)
                        log.append(f"**Patch** `{fpath}`:\n\n```diff\n{diff}\n```")
                    else:
                        log.append(f"- No changes in {fpath}")

        elif a == "add_logging":
            for fpath in py_targets:
                changed, updated, diff = add_logging_to_functions_text(fpath)
                if changed:
                    if not dry_run:
                        _write(fpath, updated)
                    log.append(f"**Patch** `{fpath}`:\n\n```diff\n{diff}\n```")
                else:
                    log.append(f"- No changes in {fpath}")

        elif a == "replace_print":
            for fpath in py_targets:
                changed, updated, diff = replace_print_with_logging_text(fpath)
                if changed:
                    if not dry_run:
                        _write(fpath, updated)
                    log.append(f"**Patch** `{fpath}`:\n\n```diff\n{diff}\n```")
                else:
                    log.append(f"- No changes in {fpath}")

        elif a == "fix_mutable_defaults":
            for fpath in py_targets:
                changed, updated, diff = fix_mutable_defaults_text(fpath)
                if changed:
                    if not dry_run:
                        _write(fpath, updated)
                    log.append(f"**Patch** `{fpath}`:\n\n```diff\n{diff}\n```")
                else:
                    log.append(f"- No changes in {fpath}")
        elif a == "noop":
            log.append("- Nothing to do.")
        else:
            log.append(f"- Unsupported action: {a}")
        log.append("")
    return "\n".join(log)
