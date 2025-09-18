import difflib

def unified_diff_text(original: str, updated: str, fromfile: str = "before", tofile: str = "after") -> str:
    a = original.splitlines(keepends=True)
    b = updated.splitlines(keepends=True)
    return "".join(difflib.unified_diff(a, b, fromfile, tofile))
