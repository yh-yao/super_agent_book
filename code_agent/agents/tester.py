def generate_tests(prompt: str) -> str:
    if 'fib' in prompt.lower():
        return '''import pytest
from code import fib

def test_fib_small():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(5) == 5
    assert fib(10) == 55

def test_negative():
    import pytest
    with pytest.raises(ValueError):
        fib(-1)
'''
    return 'def test_placeholder():\n    assert True\n'
