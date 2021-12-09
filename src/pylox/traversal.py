from typing import Callable, TypeVar

from pylox.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Grouping,
    Lambda,
    Literal,
    Logical,
    Unary,
    Variable,
)
from pylox.iexpr import Expr, Stmt
from pylox.stmt import Block, ExprStmt, Fun, If, Print, Return, Stmt, Var, While


Visitor = Callable[[Expr | Stmt], None]


class TraversalException(Exception):
    """Error while traversing"""


def visit_children(expr_or_stmt: Expr | Stmt, visit: Visitor) -> None:
    match expr_or_stmt:
        case Print(expr):
            visit(expr)
        case ExprStmt(expr):
            if expr:
                visit(expr)
        case Fun(_, _, body):
            for stmt in body:
                visit(stmt)
        case Var(_, initializer):
            if initializer:
                visit(initializer)
        case Block(stmts):
            for stmt in stmts:
                visit(stmt)
        case If(condition, if_case, else_case):
            visit(condition)
            visit(if_case)
            if else_case:
                visit(else_case)
        case While(condition, body):
            visit(condition)
            visit(body)
        case Return(_, expr):
            if expr:
                visit(expr)
        case Literal(val_expr):
            pass
        case Binary(left, _, right):
            visit(left)
            visit(right)
        case Unary(_, right):
            visit(right)
        case Logical(left, _, right):
            visit(left)
            visit(right)
        case Call(callee_expr, arg_exprs, _):
            visit(callee_expr)
            for expr in arg_exprs:
                visit(expr)
        case Grouping(expr):
            visit(expr)
        case Assign(_, val_expr):
            visit(val_expr)
        case Variable(_):
            pass
        case Lambda(_, _, body):
            for stmt in body:
                visit(stmt)
        case _:
            raise TraversalException("Unhandled expr_or_stmt", expr_or_stmt)
