from typing import Protocol

from pylox.scanner import Token


class Expr:
    pass


class NamedExpr(Protocol):
    name: Token


class Stmt:
    pass
