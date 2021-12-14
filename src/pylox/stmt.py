from dataclasses import dataclass
from typing import List

from pylox.expr import Variable
from pylox.iexpr import Expr, Stmt
from pylox.scanner import Token


@dataclass(slots=True, eq=True, frozen=True)
class ExprStmt(Stmt):
    expr: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Print(Stmt):
    expr: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr


@dataclass(slots=True, eq=True, frozen=True)
class Block(Stmt):
    stmts: List[Stmt]


@dataclass(slots=True, eq=True, frozen=True)
class If(Stmt):
    condition: Expr
    if_case: Stmt
    else_case: Stmt


@dataclass(slots=True, eq=True, frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass(slots=True, eq=True, frozen=True)
class Fun(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]


@dataclass(slots=True, eq=True, frozen=True)
class Class(Stmt):
    name: Token
    superclass: Variable
    methods: List[Fun]


@dataclass(slots=True, eq=True, frozen=True)
class Return(Stmt):
    keyword: Token
    value: Expr
