import difflib

def unified_diff_text(a: str, b: str, fromfile: str = '', tofile: str = '', lineterm: str = '\n') -> str:
    """
    Returns a string containing a unified diff of two multiline strings.
    """
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile, lineterm=lineterm)
    return "".join(diff)
