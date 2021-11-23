from typing import Dict

from pylox.error import error


class Environment:
    def __init__(self, enclosing=None):
        self._enclosing = enclosing
        self._map: Dict[str, object] = {}

    def _error(self, message: str) -> Exception:
        error("Unknown", message)
        return RuntimeError(message)

    def define(self, name: str, value: object) -> None:
        self._map[name] = value

    def assign(self, name: str, value: object) -> None:
        if name in self._map:
            self._map[name] = value
            return

        if self._enclosing:
            self._enclosing.assign(name, value)
            return

        raise self._error(f"Assigning to undefined variable {name}")

    def access(self, name: str) -> object:
        if name in self._map:
            return self._map[name]

        if self._enclosing:
            return self._enclosing.access(name)

        raise self._error(f"Attempt to access undefined variable {name}")
