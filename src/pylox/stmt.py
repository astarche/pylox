from dataclasses import dataclass
from typing import List

from pylox.iexpr import Expr, Stmt
from pylox.scanner import Token


@dataclass(slots=True)
class ExprStmt(Stmt):
    expr: Expr


@dataclass(slots=True)
class Print(Stmt):
    expr: Expr


@dataclass(slots=True)
class Var(Stmt):
    name: Token
    initializer: Expr


@dataclass(slots=True)
class Block(Stmt):
    stmts: List[Stmt]


@dataclass(slots=True)
class If(Stmt):
    condition: Expr
    if_case: Stmt
    else_case: Stmt


@dataclass(slots=True)
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass(slots=True)
class Fun(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]


@dataclass(slots=True)
class Return(Stmt):
    keyword: Token
    value: Expr
