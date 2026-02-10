import ast

from tariff_engine.domain.exceptions import UnsafeFormulaError

_ALLOWED_NODES = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.USub, ast.UAdd,
    ast.Compare, ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq,
    ast.BoolOp, ast.And, ast.Or,
    ast.IfExp,
    ast.Call,
}

_ALLOWED_FUNCTIONS = {"min", "max", "abs", "round"}


def validate_formula(expr: str) -> None:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise UnsafeFormulaError(expr, f"syntax error: {e}") from e

    for node in ast.walk(tree):
        if type(node) not in _ALLOWED_NODES:
            raise UnsafeFormulaError(expr, f"disallowed: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTIONS):
                raise UnsafeFormulaError(expr, "disallowed function call")


def eval_formula(expr: str, variables: dict[str, float]) -> float:
    validate_formula(expr)
    code = compile(ast.parse(expr, mode="eval"), "<formula>", "eval")
    namespace = dict(variables) | {
        "min": min, "max": max, "abs": abs, "round": round,
        "__builtins__": {},
    }
    return float(eval(code, namespace))
