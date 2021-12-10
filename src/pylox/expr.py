from dataclasses import dataclass, field
from typing import List

from pylox.scanner import Token
from pylox.iexpr import Stmt, Expr


@dataclass(slots=True, eq=True, frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Grouping(Expr):
    expr: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Literal(Expr):
    value: object


@dataclass(slots=True, eq=True, frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Variable(Expr):
    name: Token


@dataclass(slots=True, eq=True, frozen=True)
class Assign(Expr):
    name: Token
    value: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Call(Expr):
    callee: Expr
    args: List[Expr]
    closing_paren: Token


@dataclass(slots=True, eq=True, frozen=True)
class Lambda(Expr):
    keyword: Token
    params: List[Token]
    body: List[Stmt]


@dataclass(slots=True, eq=True, frozen=True)
class Get(Expr):
    object: Expr
    name: Token


@dataclass(slots=True, eq=True, frozen=True)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr
