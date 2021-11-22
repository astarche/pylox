from dataclasses import dataclass

from pylox.scanner import Token


class Expr:
    pass


@dataclass(slots=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(slots=True)
class Grouping(Expr):
    expr: Expr


@dataclass(slots=True)
class Literal(Expr):
    value: object


@dataclass(slots=True)
class Unary(Expr):
    operator: Token
    right: Expr
