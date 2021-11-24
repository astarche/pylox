from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Any

from pylox.error import error
from pylox.scanner import Token
from pylox.stmt import Stmt


def runtime_error(token: Token, message: str) -> Exception:
    error(token.line, message)
    return RuntimeError(message)


class LoxCallable(metaclass=ABCMeta):
    @abstractproperty
    def arity(self) -> int:
        return 0

    @abstractmethod
    def __call__(self, *args: Any) -> Any | None:
        pass

    @classmethod
    def __subclasshook__(cls, subclass: Any) -> Any:
        sub_dict = subclass.__dict__
        if "__call__" in sub_dict and "arity" in sub_dict:
            return True

        return NotImplemented
