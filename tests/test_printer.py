from pylox.parser import parse
from pylox.printer import expr_to_string
from pylox.scanner import scan_tokens


def test_print():
    expr = parse(scan_tokens("(78 * 12) + 100 + 10 * 10"))

    expr_str = expr_to_string(expr)

    assert expr_str == "(+ (+ (group (* 78.0 12.0)) 100.0) (* 10.0 10.0))"
