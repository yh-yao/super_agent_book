def generate_code(prompt: str) -> str:
    if 'fib' in prompt.lower():
        return '''def fib(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
'''
    return 'def solution(x):\n    return x\n'
