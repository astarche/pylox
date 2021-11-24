from dataclasses import dataclass
from typing import List

from pylox.scanner import Token
from pylox.iexpr import Stmt, Expr


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
    name: Variable
    value: Expr


@dataclass(slots=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(slots=True)
class Call(Expr):
    callee: Expr
    args: List[Expr]
    closing_paren: Token


@dataclass(slots=True)
class Lambda(Expr):
    keyword: Token
    params: List[Token]
    body: List[Stmt]
