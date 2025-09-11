import subprocess, sys, re

def run_pytest(workdir: str) -> str:
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=workdir, capture_output=True, text=True)
    return proc.stdout + "\n" + proc.stderr

def propose_fix(code: str, test_output: str) -> str:
    # Very naive fixer: if NameError, add stub
    m = re.search(r"NameError: name '([a-zA-Z_][a-zA-Z0-9_]*)' is not defined", test_output)
    if m:
        func = m.group(1)
        if f"def {func}" not in code:
            return code + f"\n\ndef {func}(*args, **kwargs):\n    raise NotImplementedError\n"
    return code
