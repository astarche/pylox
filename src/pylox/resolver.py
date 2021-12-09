from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Iterable, List

from pylox.error import error
from pylox.expr import Assign, Lambda, Variable
from pylox.iexpr import Expr, NamedExpr, Stmt
from pylox.scanner import Token
from pylox.stmt import Block, Fun, Var
from pylox.traversal import visit_children


Bindings = Dict[Token, int]


class _DefinedState(Enum):
    DECLARED = auto()
    DEFINED = auto()


_Scope = Dict[str, _DefinedState]


@dataclass(slots=True)
class _ResolveContext:
    scopes: List[_Scope]
    bindings: Bindings

    def __init__(self):
        self.scopes = []
        self.bindings = {}


@contextmanager
def _enter_scope(context: _ResolveContext):
    try:
        context.scopes.append({})
        yield
    finally:
        context.scopes.pop()


def _resolve_children(expr_or_stmt: Expr | Stmt, context: _ResolveContext) -> None:
    visit_children(expr_or_stmt, lambda child_expr_or_stmt: _resolve(child_expr_or_stmt, context))


def _declare(name: Token, context: _ResolveContext):
    if not context.scopes:
        return
    scope = context.scopes[-1]
    if name.lexeme in scope:
        error(name.line, f"Redefinition of {name.lexeme}.")
    else:
        scope[name.lexeme] = _DefinedState.DECLARED


def _define(name: Token, context: _ResolveContext):
    if not context.scopes:
        return
    scope = context.scopes[-1]
    scope[name.lexeme] = _DefinedState.DEFINED


def _bind(reference: NamedExpr, context: _ResolveContext):
    name_token = reference.name
    for i, scope in enumerate(reversed(context.scopes), 1):
        match scope.get(name_token.lexeme):
            case _DefinedState.DEFINED:
                context.bindings[name_token] = -i
                break
            case _DefinedState.DECLARED:
                error(
                    name_token.line,
                    f"Cannot bind reference to {name_token.lexeme} during definition.",
                )
                break
            case None:
                continue


def _resolve(expr_or_stmt: Expr | Stmt, context: _ResolveContext):
    match expr_or_stmt:
        case Block(_):
            with _enter_scope(context):
                _resolve_children(expr_or_stmt, context)
        case Var(name, _):
            _declare(name, context)
            _resolve_children(expr_or_stmt, context)
            _define(name, context)
        case Variable(name) as variable:
            _bind(variable, context)
        case Assign(name, _) as assignment:
            _bind(assignment, context)
            _resolve_children(expr_or_stmt, context)
        case Fun(name, params, _):
            _declare(name, context)
            _define(name, context)
            with _enter_scope(context):
                for p in params:
                    _declare(p, context)
                    _define(p, context)
                _resolve_children(expr_or_stmt, context)
        case Lambda(_, params, _):
            with _enter_scope(context):
                for p in params:
                    _declare(p, context)
                    _define(p, context)
                _resolve_children(expr_or_stmt, context)
        case _:
            _resolve_children(expr_or_stmt, context)


def resolve(program: Iterable[Stmt]) -> Bindings:
    context = _ResolveContext()
    for stmt in program:
        _resolve(stmt, context)
    return context.bindings
