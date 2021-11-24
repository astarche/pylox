from typing import Iterable

from pylox.environment import Environment
from pylox.expr import Assign, Binary, Expr, Grouping, Literal, Logical, Unary, Variable
from pylox.stmt import Block, ExprStmt, If, Print, Stmt, Var, While


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


def _interpret(expr_or_stmt: Expr | Stmt, env: Environment) -> object | None:
    match expr_or_stmt:
        case Print(expr):
            print(_stringify(_interpret(expr, env)))
        case ExprStmt(expr):
            _interpret(expr, env)
        case Var(name, None):
            env.define(name.lexeme, None)
        case Var(name, initializer):
            env.define(name.lexeme, _interpret(initializer, env))
        case Block(stmts):
            block_env = Environment(env)
            for stmt in stmts:
                _interpret(stmt, block_env)
        case If(condition, if_case, else_case):
            if _interpret(condition, env):
                _interpret(if_case, env)
            elif else_case:
                _interpret(else_case, env)
        case While(condition, body):
            while _is_truthy(_interpret(condition, env)):
                _interpret(body, env)
        case Literal(val_expr):
            return val_expr
        case Binary(left, operator, right):
            lhs = _interpret(left, env)
            rhs = _interpret(right, env)
            match operator.lexeme:
                case "+":
                    return lhs + rhs
                case "-":
                    return lhs - rhs
                case "*":
                    return lhs * rhs
                case "/":
                    return lhs / rhs
                case "<":
                    return lhs < rhs
                case ">":
                    return lhs > rhs
                case "<=":
                    return lhs <= rhs
                case ">=":
                    return lhs >= rhs
                case "==":
                    return lhs == rhs
                case "!=":
                    return lhs != rhs
                case _:
                    raise RuntimeError(f"({operator.line}) Unrecognized operator {operator.lexeme}")
        case Unary(operator, right):
            rhs = _interpret(right, env)
            match operator.lexeme:
                case "!":
                    return not _is_truthy(rhs)
                case "-":
                    return -rhs
        case Logical(left, operator, right):
            lhs = _interpret(left, env)
            match operator.lexeme:
                case "and":
                    if not _is_truthy(lhs):
                        return lhs
                case "or":
                    if _is_truthy(lhs):
                        return lhs
            return _interpret(right, env)
        case Grouping(expr):
            return _interpret(expr, env)
        case Assign(name, val_expr):
            val = _interpret(val_expr, env)
            env.assign(name.lexeme, val)
            return val
        case Variable(name):
            return env.access(name.lexeme)


def interpret(stmts: Iterable[Stmt], env: Environment) -> None:
    try:
        for stmt in stmts:
            _interpret(stmt, env)
    except RuntimeError:
        pass
