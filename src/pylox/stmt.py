from dataclasses import dataclass

from pylox.expr import Expr


class Stmt:
    pass


@dataclass(slots=True)
class ExprStmt:
    expr: Expr


@dataclass(slots=True)
class Print:
    expr: Expr
