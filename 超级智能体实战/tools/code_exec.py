
import ast, math

_ALLOWED_NAMES = {k:getattr(math,k) for k in dir(math) if not k.startswith("_")}
_ALLOWED_NAMES.update({"True": True, "False": False, "None": None})

class SafeEvalVisitor(ast.NodeVisitor):
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
        ast.Name, ast.Load, ast.Dict, ast.List, ast.Tuple, ast.Set,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.USub, ast.UAdd, ast.Call, ast.keyword, ast.Compare,
        ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Eq, ast.NotEq, ast.And, ast.Or,
        ast.BoolOp, ast.IfExp
    )

    def visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            raise ValueError(f"Unsafe or unsupported syntax: {type(node).__name__}")
        return super().visit(node)

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct calls to allowed math functions are permitted")
        if node.func.id not in _ALLOWED_NAMES:
            raise ValueError(f"Function '{node.func.id}' is not allowed")
        for arg in node.args: self.visit(arg)
        for kw in node.keywords: self.visit(kw.value)

def safe_eval(expr: str):
    tree = ast.parse(expr, mode="eval")
    SafeEvalVisitor().visit(tree)
    code = compile(tree, "<expr>", "eval")
    return eval(code, {"__builtins__": {}}, _ALLOWED_NAMES)
