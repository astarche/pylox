from dataclasses import dataclass
from typing import Any, Any, Iterable, List

from pylox.environment import Environment
from pylox.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Grouping,
    Lambda,
    Literal,
    Logical,
    Unary,
    Variable,
)
from pylox.scanner import Token
from pylox.runtime import LoxCallable, runtime_error
from pylox.stmt import Block, ExprStmt, Fun, If, Print, Return, Stmt, Var, While


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


@dataclass
class _ReturnValue(Exception):
    value: Any | None


def _interpret(expr_or_stmt: Expr | Stmt, env: Environment) -> object | None:
    match expr_or_stmt:
        case Print(expr):
            print(_stringify(_interpret(expr, env)))
        case ExprStmt(expr):
            _interpret(expr, env)
        case Var(name, None):
            env.define(name, None)
        case Fun(name, params, body):
            env.define(name, LoxFunction(params, body, env))
        case Var(name, initializer):
            env.define(name, _interpret(initializer, env))
        case Block(stmts):
            interpret_block(stmts, Environment(env))
        case If(condition, if_case, else_case):
            if _interpret(condition, env):
                _interpret(if_case, env)
            elif else_case:
                _interpret(else_case, env)
        case While(condition, body):
            while _is_truthy(_interpret(condition, env)):
                _interpret(body, env)
        case Return(_, None):
            raise _ReturnValue(None)
        case Return(_, expr):
            raise _ReturnValue(_interpret(expr, env))
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
                    raise runtime_error(operator, f"Unrecognized operator {operator.lexeme}")
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
        case Call(callee_expr, arg_exprs, closing_paren):
            func = _interpret(callee_expr, env)
            if not isinstance(func, LoxCallable):
                raise runtime_error(closing_paren, "Callee is not a function!")
            if func.arity != len(arg_exprs):
                raise runtime_error(closing_paren, "Wrong nargs!")
            return func(*[_interpret(a, env) for a in arg_exprs])
        case Grouping(expr):
            return _interpret(expr, env)
        case Assign(name, val_expr):
            val = _interpret(val_expr, env)
            env.assign(name, val)
            return val
        case Variable(name):
            return env.access(name)
        case Lambda(_, params, body):
            return LoxFunction(params, body, env)


@dataclass(slots=True)
class LoxFunction:
    params: List[Token]
    body: List[Stmt]
    env: Environment

    @property
    def arity(self) -> int:
        return len(self.params)

    def __call__(self, *args):
        call_env = Environment(self.env)
        for token, value in zip(self.params, args):
            call_env.define(token, value)

        try:
            interpret_block(self.body, call_env)
        except _ReturnValue as ret:
            return ret.value
        return None


def interpret_block(stmts: Iterable[Stmt], env: Environment) -> None:
    for stmt in stmts:
        _interpret(stmt, env)


def interpret(stmts: Iterable[Stmt], env: Environment) -> None:
    try:
        interpret_block(stmts, env)
    except RuntimeError:
        pass
