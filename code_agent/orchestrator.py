import os, sys
from agents.coder import generate_code
from agents.tester import generate_tests
from agents.debugger import run_pytest, propose_fix

def main(task: str):
    os.makedirs("workspace", exist_ok=True)
    code = generate_code(task)
    tests = generate_tests(task)
    with open("workspace/code.py", "w", encoding="utf-8") as f:
        f.write(code)
    with open("workspace/test_code.py", "w", encoding="utf-8") as f:
        f.write(tests)

    print("== Running tests ==")
    out = run_pytest("workspace")
    print(out)

    if "FAILED" in out:
        print("== Attempting naive fix ==")
        fixed = propose_fix(code, out)
        with open("workspace/code.py", "w", encoding="utf-8") as f:
            f.write(fixed)
        out = run_pytest("workspace")
        print(out)

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Write a function fib(n)"
    main(task)
