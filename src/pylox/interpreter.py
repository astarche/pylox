from typing import Iterable

from pylox.expr import Binary, Expr, Grouping, Literal, Unary
from pylox.stmt import ExprStmt, Print, Stmt


def _is_truthy(val: object):
    return val not in [False, None]


def _stringify(val: object) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"

    if val == None:
        return "nil"

    if isinstance(val, float):
        str_val = str(val)
        return str_val[:-2] if str_val.endswith(".0") else str_val

    return str(val)


def _interpret(expr_or_stmt: Expr | Stmt) -> object | None:
    match expr_or_stmt:
        case Print(expr):
            print(_stringify(_interpret(expr)))
        case ExprStmt(expr):
            _interpret(expr)
        case Literal(value):
            return value
        case Binary(left, operator, right):
            lhs = _interpret(left)
            rhs = _interpret(right)
            match operator.lexeme:
                case "+":
                    return lhs + rhs
                case "-":
                    return lhs - rhs
                case "*":
                    return lhs * rhs
                case "/":
                    return lhs / rhs
        case Unary(operator, right):
            rhs = _interpret(right)
            match operator.lexeme:
                case "!":
                    return not _is_truthy(rhs)
                case "-":
                    return -rhs
        case Grouping(expr):
            return _interpret(expr)


def interpret(stmts: Iterable[Stmt]) -> None:
    for stmt in stmts:
        _interpret(stmt)
