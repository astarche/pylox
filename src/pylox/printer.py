from pylox.expr import Expr, Literal, Unary, Binary, Grouping


def _parenthesize(name: str, *exprs: Expr) -> str:
    return f"({name} {str.join(' ', (expr_to_string(e) for e in exprs))})"


def print_expr(expr: Expr) -> None:
    print(expr_to_string(expr))


def expr_to_string(expr: Expr) -> str:
    match expr:
        case Literal(value):
            return str(value)
        case Binary(left, operator, right):
            return _parenthesize(operator.lexeme, left, right)
        case Unary(operator, right):
            return _parenthesize(operator.lexeme, right)
        case Grouping(expr):
            return _parenthesize("group", expr)
