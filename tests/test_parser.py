from typing import List

from pylox.stmt import Stmt
from pylox.expr import Expr, Literal
from pylox.parser import parse_expr, parse
from pylox.scanner import TokenType, scan_tokens


def _scan_and_parse_expr(input: str) -> Expr:
    return parse_expr(scan_tokens(input))


def _scan_and_parse_program(input: str) -> List[Stmt]:
    return list(parse(scan_tokens(input)))


def test_primary():
    inputs = ["123", "false", "true", "nil", '"Hello"', "45.78"]
    exprs = [_scan_and_parse_expr(i) for i in inputs]

    assert all(isinstance(e, Literal) for e in exprs)
    assert [e.value for e in exprs] == [123, False, True, None, "Hello", 45.78]


def test_unary_minus():
    expr = _scan_and_parse_expr("-12.09")

    assert expr.operator.token == TokenType.MINUS
    assert expr.right.value == 12.09


def test_bin_op():
    op_map = {"+": TokenType.PLUS, "-": TokenType.MINUS, "/": TokenType.SLASH, "*": TokenType.STAR}
    exprs = [_scan_and_parse_expr(f"45 {op} 55") for op in op_map]

    for expr, operator in zip(exprs, op_map.values()):
        assert expr.left.value == 45
        assert expr.operator.token == operator
        assert expr.right.value == 55


def test_composite():
    expr = _scan_and_parse_expr("(78 * 12) + 100 + 10 * 10")

    assert expr.left.left.expr.left.value == 78
    assert expr.right.left.value == 10
    assert expr.left.right.value == 100


def test_stmt():
    prog = _scan_and_parse_program(
        """
print 1 + 2 + 3;
print "Hello World";
(3 + 1) * (10 / 10) + 50.45;
"""
    )

    assert len(prog) == 3
    assert prog[0].expr.left.left.value == 1.0
    assert prog[1].expr.value == "Hello World"
    assert prog[2].expr.right.value == 50.45
