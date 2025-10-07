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
        _print(f"分析结果已写入 {args.out}")
    else:
        _print(md)

def cmd_plan(args):
    root = load_input_to_workspace(args.path, None)
    steps = parse_instruction_to_plan(args.instruction)
    md = render_plan_markdown(steps)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        _print(f"计划已写入 {args.out}")
    else:
        _print(md)

def cmd_edit(args):
    root = load_input_to_workspace(args.path, None)
    steps = parse_instruction_to_plan(args.instruction or "")

    files = list_files(root)
    log_path = new_log_path(root, prefix="edit")
    md = ["# 智能编程助手编辑日志", f"- 根目录: `{root}`", f"- 应用更改: {args.apply}", ""]
    md.append("## 计划")
    md.append(render_plan_markdown(steps))
    md.append("## 执行")
    result = apply_actions(root, files, steps, dry_run=(not args.apply))
    md.append(result)

    text = "\n".join(md)
    write_log(log_path, text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        _print(f"编辑日志已写入 {args.out}")
    else:
        _print(text)
    _print(f"完整日志已保存: {log_path}")

def cmd_verify(args):
    root = load_input_to_workspace(args.path, None)
    files = [f for f in list_files(root) if f.endswith(".py")]
    ok = True
    msgs = []
    for py in files:
        proc = subprocess.run([sys.executable, "-m", "py_compile", py], capture_output=True, text=True)
        if proc.returncode != 0:
            ok = False
            msgs.append(f"[失败] {py}: {proc.stderr.strip()}")
        else:
            msgs.append(f"[通过]   {py}")
    _print("\n".join(msgs))
    _print("验证: 通过" if ok else "验证: 失败")
    if not ok:
        sys.exit(1)

def cmd_auto(args):
    """协调分析、规划、编辑和验证的序列。"""
    root = load_input_to_workspace(args.path, None)
    log_path = new_log_path(root, prefix="auto")
    md = ["# 智能编程助手自动日志", f"- 根目录: `{root}`", f"- 指令: `{args.instruction}`", f"- 应用更改: {args.apply}", ""]

    # 1. 分析
    _print("### 1. 正在分析代码库...")
    analysis_data = analyze(root)
    
    # 日志的初始分析
    analysis_md = render_markdown_report(analysis_data, include_code=False)
    md.append("## 分析")
    md.append(analysis_md)
    _print("分析完成。")

    # 计划和编辑的循环
    steps = []
    dry_run_result = ""
    max_retries = 3
    for i in range(max_retries):
        # 为LLM创建丰富的上下文
        rich_analysis_md = render_markdown_report(analysis_data, include_code=True)
        
        # 2. 计划
        _print(f"\n### 2. 正在生成计划（尝试 {i+1}/{max_retries}）...")
        steps = parse_instruction_to_plan(args.instruction, rich_analysis_md)
        plan_md = render_plan_markdown(steps)
        md.append(f"## 计划（尝试 {i+1}）")
        md.append(plan_md)
        _print("计划:")
        _print(plan_md)

        # 3. 编辑（试运行）
        _print("\n### 3. 正在应用编辑（试运行）...")
        files = list_files(root)
        dry_run_result = apply_actions(root, files, steps, dry_run=True)
        md.append(f"## 执行（试运行，尝试 {i+1}）")
        md.append(dry_run_result)
        _print(dry_run_result)

        if "- 错误:" in dry_run_result or "- Error:" in dry_run_result:
            _print("\n计划应用失败。正在重新分析和规划...")
            # 为下次尝试更新分析，添加失败上下文
            analysis_data['files'].append({'path': 'error_log', 'lang': 'text', 'content': dry_run_result})
            if i == max_retries - 1:
                _print("\n已达到最大重试次数。中止。")
                text = "\n".join(md)
                write_log(log_path, text)
                _print(f"完整日志已保存: {log_path}")
                sys.exit(1)
            continue
        else:
            break

    if not args.apply:
        _print("\n试运行完成。使用 --apply 将更改写入磁盘。")
        text = "\n".join(md)
        write_log(log_path, text)
        _print(f"完整日志已保存: {log_path}")
        return

    # 4. 编辑（应用）
    _print("\n### 4. 正在将编辑应用到磁盘...")
    files = list_files(root)
    apply_result = apply_actions(root, files, steps, dry_run=False)
    md.append("## 执行（应用）")
    md.append(apply_result)
    _print(apply_result)
    _print("编辑已应用。")

    # 5. 验证
    _print("\n### 5. 正在验证更改...")
    files_to_verify = [f for f in list_files(root) if f.endswith(".py")]
    ok = True
    msgs = []
    for py in files_to_verify:
        proc = subprocess.run([sys.executable, "-m", "py_compile", py], capture_output=True, text=True)
        if proc.returncode != 0:
            ok = False
            msgs.append(f"[失败] {py}: {proc.stderr.strip()}")
        else:
            msgs.append(f"[通过]   {py}")
    verification_result = "\n".join(msgs)
    md.append("## 验证")
    md.append(verification_result)
    _print(verification_result)
    _print("验证: 通过" if ok else "验证: 失败")

    text = "\n".join(md)
    write_log(log_path, text)
    _print(f"\n完整日志已保存: {log_path}")

    if not ok:
        sys.exit(1)

def main():
    p = argparse.ArgumentParser(prog="smartcoder", description="逐步代码分析和编辑智能体（仅使用标准库）。")
    sub = p.add_subparsers()

    pa = sub.add_parser("analyze", help="分析路径/zip文件/文件中的代码或代码片段")
    pa.add_argument("path", nargs="?", help="文件/目录/zip的路径")
    pa.add_argument("--code", help="分析代码片段")
    pa.add_argument("-o", "--out", help="将markdown报告写入文件")
    pa.set_defaults(func=cmd_analyze)

    pp = sub.add_parser("plan", help="根据指令创建逐步计划")
    pp.add_argument("-p", "--path", required=True, help="文件/目录/zip的路径")
    pp.add_argument("-i", "--instruction", required=True, help="自由形式指令，例如：'将print替换为logging'")
    pp.add_argument("-o", "--out", help="将计划写入文件")
    pp.set_defaults(func=cmd_plan)

    pe = sub.add_parser("edit", help="应用编辑（默认为试运行）")
    pe.add_argument("-p", "--path", required=True, help="文件/目录/zip的路径")
    pe.add_argument("-i", "--instruction", help="自由形式指令")
    pe.add_argument("--apply", action="store_true", help="将更改写入磁盘（默认为试运行）")
    pe.add_argument("-o", "--out", help="将执行日志写入文件")
    pe.set_defaults(func=cmd_edit)

    pv = sub.add_parser("verify", help="语法检查（.py）文件")
    pv.add_argument("-p", "--path", required=True, help="文件/目录/zip的路径")
    pv.set_defaults(func=cmd_verify)

    p_auto = sub.add_parser("auto", help="根据指令自动分析、规划、编辑和验证")
    p_auto.add_argument("-p", "--path", required=True, help="文件/目录/zip的路径")
    p_auto.add_argument("-i", "--instruction", required=True, help="自由形式指令，例如：'将print替换为logging'")
    p_auto.add_argument("--apply", action="store_true", help="将更改写入磁盘（默认为试运行）")
    p_auto.set_defaults(func=cmd_auto)

    args = p.parse_args()
    if not hasattr(args, "func"):
        p.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
