from time import time
from typing import Dict

from pylox.runtime import runtime_error
from pylox.scanner import Token


class Environment:
    def __init__(self, enclosing=None):
        self._enclosing = enclosing
        self._map: Dict[str, object] = {}

    def define(self, name: str | Token, value: object) -> None:
        name = name if isinstance(name, str) else name.lexeme
        self._map[name] = value

    def assign(self, name_token: Token, value: object) -> None:
        name = name_token.lexeme
        if name in self._map:
            self._map[name] = value
            return

        if self._enclosing:
            self._enclosing.assign(name_token, value)
            return

        raise runtime_error(name_token, f"Assigning to undefined variable {name}")

    def access(self, name_token: Token) -> object:
        name = name_token.lexeme
        if name in self._map:
            return self._map[name]

        if self._enclosing:
            return self._enclosing.access(name_token)

        raise runtime_error(name_token, f"Attempt to access undefined variable {name}")


class _Clock:
    arity = 0

    def __call__(self):
        return time() / 1000.0


def init_global_env() -> Environment:
    env = Environment()
    env.define("clock", _Clock())
    return env
