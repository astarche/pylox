from dataclasses import dataclass

from pylox.expr import Expr
from pylox.scanner import Token


class Stmt:
    pass


@dataclass(slots=True)
class ExprStmt:
    expr: Expr


@dataclass(slots=True)
class Print:
    expr: Expr


@dataclass(slots=True)
class Var:
    name: Token
    initializer: Expr
