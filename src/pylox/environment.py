from time import time
from typing import Dict, List
from pylox.iexpr import Expr, NamedExpr
from pylox.resolver import Bindings

from pylox.runtime import runtime_error
from pylox.scanner import Token

_ValMap = Dict[str, object]
_GLOBAL_SCOPE_INDEX = 0


class Environment:
    def __init__(self, bindings: Bindings = {}):
        self._bindings = bindings
        self._map: List[_ValMap] = [{}]

    def _resolve_bound_scope(self, expr: NamedExpr) -> _ValMap:
        scope_index = self._bindings.get(expr.name, _GLOBAL_SCOPE_INDEX)
        return self._map[scope_index]

    def create_child(self):
        env = Environment(self._bindings)
        env._map = self._map + env._map
        return env

    def merge_bindings(self, bindings: Bindings):
        self._bindings.update(bindings)

    def define(self, name: str | Token, value: object) -> None:
        name = name if isinstance(name, str) else name.lexeme
        self._map[-1][name] = value

    def assign(self, named_expr: NamedExpr, value: object) -> None:
        name = named_expr.name.lexeme
        scope = self._resolve_bound_scope(named_expr)

        if name in scope:
            scope[name] = value
            return

        raise runtime_error(named_expr.name, f"Assigning to undefined variable {name}")

    def access(self, named_expr: NamedExpr) -> object:
        name = named_expr.name.lexeme

        scope = self._resolve_bound_scope(named_expr)

        if name in scope:
            return scope[name]

        raise runtime_error(named_expr.name, f"Attempt to access undefined variable {name}")


class _Clock:
    arity = 0

    def __call__(self):
        return time() / 1000.0


def init_global_env() -> Environment:
    env = Environment()
    env.define("clock", _Clock())
    return env
