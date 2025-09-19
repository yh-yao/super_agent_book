import argparse, os, sys, subprocess, time, pathlib
from .workspace import load_input_to_workspace, list_files
from .analyzer import analyze, render_markdown_report
from .planner import parse_instruction_to_plan, render_plan_markdown
from .editor import apply_actions

def new_log_path(root: str, prefix: str = "run") -> str:
    log_dir = os.path.join(root, ".smartcoder", "logs")
    os.makedirs(log_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    return os.path.join(log_dir, f"{prefix}-{ts}.md")

def write_log(path: str, content: str) -> None:
    base = pathlib.Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content if content.endswith("\n") else content + "\n")

def _print(s: str):
    if s is None:
        s = ""
    sys.stdout.write(s + ("\n" if not s.endswith("\n") else ""))
    sys.stdout.flush()

def cmd_analyze(args):
    root = load_input_to_workspace(args.path, args.code)
    data = analyze(root)
    md = render_markdown_report(data)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        _print(f"Analysis written to {args.out}")
    else:
        _print(md)

def cmd_plan(args):
    root = load_input_to_workspace(args.path, None)
    steps = parse_instruction_to_plan(args.instruction)
    md = render_plan_markdown(steps)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        _print(f"Plan written to {args.out}")
    else:
        _print(md)

def cmd_edit(args):
    root = load_input_to_workspace(args.path, None)
    steps = parse_instruction_to_plan(args.instruction or "")

    files = list_files(root)
    log_path = new_log_path(root, prefix="edit")
    md = ["# SmartCoder Edit Log", f"- Root: `{root}`", f"- Apply: {args.apply}", ""]
    md.append("## Plan")
    md.append(render_plan_markdown(steps))
    md.append("## Execution")
    result = apply_actions(root, files, steps, dry_run=(not args.apply))
    md.append(result)

    text = "\n".join(md)
    write_log(log_path, text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        _print(f"Edit log written to {args.out}")
    else:
        _print(text)
    _print(f"Full log saved: {log_path}")

def cmd_verify(args):
    root = load_input_to_workspace(args.path, None)
    files = [f for f in list_files(root) if f.endswith(".py")]
    ok = True
    msgs = []
    for py in files:
        proc = subprocess.run([sys.executable, "-m", "py_compile", py], capture_output=True, text=True)
        if proc.returncode != 0:
            ok = False
            msgs.append(f"[FAIL] {py}: {proc.stderr.strip()}")
        else:
            msgs.append(f"[OK]   {py}")
    _print("\n".join(msgs))
    _print("Verification: PASSED" if ok else "Verification: FAILED")
    if not ok:
        sys.exit(1)

def cmd_auto(args):
    """Orchestrates the analyze, plan, edit, and verify sequence."""
    root = load_input_to_workspace(args.path, None)
    log_path = new_log_path(root, prefix="auto")
    md = ["# SmartCoder Auto Log", f"- Root: `{root}`", f"- Instruction: `{args.instruction}`", f"- Apply: {args.apply}", ""]

    # 1. Analyze
    _print("### 1. Analyzing codebase...")
    analysis_data = analyze(root)
    
    # Initial analysis for the log
    analysis_md = render_markdown_report(analysis_data, include_code=False)
    md.append("## Analysis")
    md.append(analysis_md)
    _print("Analysis complete.")

    # Loop for plan and edit
    steps = []
    dry_run_result = ""
    max_retries = 3
    for i in range(max_retries):
        # Create a rich context for the LLM
        rich_analysis_md = render_markdown_report(analysis_data, include_code=True)
        
        # 2. Plan
        _print(f"\n### 2. Generating a plan (Attempt {i+1}/{max_retries})...")
        steps = parse_instruction_to_plan(args.instruction, rich_analysis_md)
        plan_md = render_plan_markdown(steps)
        md.append(f"## Plan (Attempt {i+1})")
        md.append(plan_md)
        _print("Plan:")
        _print(plan_md)

        # 3. Edit (dry-run)
        _print("\n### 3. Applying edits (dry-run)...")
        files = list_files(root)
        dry_run_result = apply_actions(root, files, steps, dry_run=True)
        md.append(f"## Execution (Dry-run, Attempt {i+1})")
        md.append(dry_run_result)
        _print(dry_run_result)

        if "- Error:" in dry_run_result:
            _print("\nPlan failed to apply. Re-analyzing and re-planning...")
            # Update analysis with failure context for the next attempt
            analysis_data['files'].append({'path': 'error_log', 'lang': 'text', 'content': dry_run_result})
            if i == max_retries - 1:
                _print("\nMax retries reached. Aborting.")
                text = "\n".join(md)
                write_log(log_path, text)
                _print(f"Full log saved: {log_path}")
                sys.exit(1)
            continue
        else:
            break

    if not args.apply:
        _print("\nDry-run complete. Use --apply to write changes to disk.")
        text = "\n".join(md)
        write_log(log_path, text)
        _print(f"Full log saved: {log_path}")
        return

    # 4. Edit (apply)
    _print("\n### 4. Applying edits to disk...")
    files = list_files(root)
    apply_result = apply_actions(root, files, steps, dry_run=False)
    md.append("## Execution (Apply)")
    md.append(apply_result)
    _print(apply_result)
    _print("Edits applied.")

    # 5. Verify
    _print("\n### 5. Verifying changes...")
    files_to_verify = [f for f in list_files(root) if f.endswith(".py")]
    ok = True
    msgs = []
    for py in files_to_verify:
        proc = subprocess.run([sys.executable, "-m", "py_compile", py], capture_output=True, text=True)
        if proc.returncode != 0:
            ok = False
            msgs.append(f"[FAIL] {py}: {proc.stderr.strip()}")
        else:
            msgs.append(f"[OK]   {py}")
    verification_result = "\n".join(msgs)
    md.append("## Verification")
    md.append(verification_result)
    _print(verification_result)
    _print("Verification: PASSED" if ok else "Verification: FAILED")

    text = "\n".join(md)
    write_log(log_path, text)
    _print(f"\nFull log saved: {log_path}")

    if not ok:
        sys.exit(1)

def main():
    p = argparse.ArgumentParser(prog="smartcoder", description="Step-by-step code analysis and editing agent (stdlib-only).")
    sub = p.add_subparsers()

    pa = sub.add_parser("analyze", help="Analyze code at a path/zip/file or from a snippet")
    pa.add_argument("path", nargs="?", help="path to file/dir/zip")
    pa.add_argument("--code", help="analyze a code snippet instead")
    pa.add_argument("-o", "--out", help="write markdown report to file")
    pa.set_defaults(func=cmd_analyze)

    pp = sub.add_parser("plan", help="Create a step-by-step plan from an instruction")
    pp.add_argument("-p", "--path", required=True, help="path to file/dir/zip")
    pp.add_argument("-i", "--instruction", required=True, help="free-form instruction, e.g., 'replace print with logging'")
    pp.add_argument("-o", "--out", help="write plan to file")
    pp.set_defaults(func=cmd_plan)

    pe = sub.add_parser("edit", help="Apply edits (dry-run by default)")
    pe.add_argument("-p", "--path", required=True, help="path to file/dir/zip")
    pe.add_argument("-i", "--instruction", help="free-form instruction")
    pe.add_argument("--apply", action="store_true", help="write changes to disk (default is dry-run)")
    pe.add_argument("-o", "--out", help="write execution log to file")
    pe.set_defaults(func=cmd_edit)

    pv = sub.add_parser("verify", help="Syntax check (.py) files")
    pv.add_argument("-p", "--path", required=True, help="path to file/dir/zip")
    pv.set_defaults(func=cmd_verify)

    p_auto = sub.add_parser("auto", help="Automatically analyze, plan, edit, and verify based on an instruction")
    p_auto.add_argument("-p", "--path", required=True, help="path to file/dir/zip")
    p_auto.add_argument("-i", "--instruction", required=True, help="free-form instruction, e.g., 'replace print with logging'")
    p_auto.add_argument("--apply", action="store_true", help="write changes to disk (default is dry-run)")
    p_auto.set_defaults(func=cmd_auto)

    args = p.parse_args()
    if not hasattr(args, "func"):
        p.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
