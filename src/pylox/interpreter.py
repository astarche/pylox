from dataclasses import dataclass, field
from typing import Any, Any, Dict, Iterable, List

from pylox.environment import Environment
from pylox.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Lambda,
    Literal,
    Logical,
    This,
    Unary,
    Variable,
    Set,
)
from pylox.scanner import Token
from pylox.runtime import LoxCallable, runtime_error
from pylox.stmt import Block, Class, ExprStmt, Fun, If, Print, Return, Stmt, Var, While


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
        case Var(name, initializer):
            env.define(name, _interpret(initializer, env))
        case Class(name, superclass_var, method_stmts) as class_expr:
            env.define(name, None)
            superclass = _interpret(superclass_var, env)
            methods: Dict[str, LoxFunction] = {}
            for method in method_stmts:
                methods[method.name.lexeme] = LoxFunction(method.params, method.body, env)
            klass = LoxClass(name.lexeme, superclass, methods)
            env.assign(class_expr, klass)
        case Fun(name, params, body):
            env.define(name, LoxFunction(params, body, env))
        case Block(stmts):
            interpret_block(stmts, env.create_child())
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
        case Assign(name, val_expr) as assign_var:
            val = _interpret(val_expr, env)
            env.assign(assign_var, val)
            return val
        case Variable(name) as var:
            return env.access(var)
        case Lambda(_, params, body):
            return LoxFunction(params, body, env)
        case Get(obj_expr, name):
            obj_val = _interpret(obj_expr, env)
            if isinstance(obj_val, LoxInstance):
                return obj_val[name]
            else:
                raise runtime_error(name, "Only instances have fields.")
        case Set(obj_expr, name, val_expr):
            obj_val = _interpret(obj_expr, env)
            if isinstance(obj_val, LoxInstance):
                obj_val[name] = _interpret(val_expr, env)
            else:
                raise runtime_error(name, "Only instances have fields.")
        case This(_) as this_expr:
            return env.access(this_expr)


@dataclass(slots=True)
class LoxFunction:
    params: List[Token]
    body: List[Stmt]
    env: Environment

    @property
    def arity(self) -> int:
        return len(self.params)

    def __call__(self, *args):
        call_env = self.env.create_child()
        for token, value in zip(self.params, args):
            call_env.define(token, value)

        try:
            interpret_block(self.body, call_env)
        except _ReturnValue as ret:
            return ret.value
        return None


@dataclass(slots=True)
class LoxClass:
    name: str
    superclass: Any  # LoxClass
    methods: Dict[str, LoxFunction]

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, *args):
        return LoxInstance(self)

    def __str__(self):
        return self.name


def _lookup_method(klass: LoxClass, name: str) -> LoxFunction:
    if name in klass.methods:
        return klass.methods[name]
    if klass.superclass:
        return _lookup_method(klass.superclass, name)


@dataclass(slots=True)
class LoxInstance:
    klass: LoxClass
    fields: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: Token):
        key_str = key.lexeme
        if key_str in self.fields:
            return self.fields[key_str]

        if method := _lookup_method(self.klass, key_str):
            return _bind(method, self)

        raise runtime_error(key, "Undefined property.")

    def __setitem__(self, key: Token, value):
        self.fields[key.lexeme] = value

    def __str__(self):
        return self.klass.name + " instance"


def _bind(function: LoxFunction, instance: LoxInstance):
    env = function.env.create_child()
    env.define("this", instance)
    return LoxFunction(function.params, function.body, env)


def interpret_block(stmts: Iterable[Stmt], env: Environment) -> None:
    for stmt in stmts:
        _interpret(stmt, env)


def interpret(stmts: Iterable[Stmt], env: Environment) -> None:
    try:
        interpret_block(stmts, env)
    except RuntimeError:
        pass
