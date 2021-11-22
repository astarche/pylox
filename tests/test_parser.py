from pylox.expr import Expr, Literal
from pylox.parser import parse
from pylox.scanner import TokenType, scan_tokens


def _scan_and_parse(input: str) -> Expr:
    return parse(scan_tokens(input))


def test_primary():
    inputs = ["123", "false", "true", "nil", '"Hello"', "45.78"]
    exprs = [_scan_and_parse(i) for i in inputs]

    assert all(isinstance(e, Literal) for e in exprs)
    assert [e.value for e in exprs] == [123, False, True, None, "Hello", 45.78]


def test_unary_minus():
    expr = _scan_and_parse("-12.09")

    assert expr.operator.token == TokenType.MINUS
    assert expr.right.value == 12.09


def test_bin_op():
    op_map = {"+": TokenType.PLUS, "-": TokenType.MINUS, "/": TokenType.SLASH, "*": TokenType.STAR}
    exprs = [_scan_and_parse(f"45 {op} 55") for op in op_map]

    for expr, operator in zip(exprs, op_map.values()):
        assert expr.left.value == 45
        assert expr.operator.token == operator
        assert expr.right.value == 55


def test_composite():
    expr = _scan_and_parse("(78 * 12) + 100 + 10 * 10")

    assert expr.left.left.expr.left.value == 78
    assert expr.right.left.value == 10
    assert expr.left.right.value == 100
