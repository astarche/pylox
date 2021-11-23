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


@dataclass(slots=True)
class Variable(Expr):
    name: Token


@dataclass(slots=True)
class Assign(Expr):
    name: str
    value: Expr
