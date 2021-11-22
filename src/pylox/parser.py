from typing import Iterable, Optional

from pylox.error import error
from pylox.expr import Binary, Expr, Grouping, Unary, Literal
from pylox.scanner import Token, TokenType


class _ParseView:
    def __init__(self, tokens: Iterable[Token]):
        self._tokens = list(tokens)
        self._current = 0

    def is_at_end(self) -> bool:
        return self._current >= len(self._tokens)

    def peek(self) -> Token:
        if self.is_at_end():
            return None
        return self._tokens[self._current]

    def advance(self) -> Token:
        val = self.peek()
        self._current += 1
        return val

    def match(self, *tokens: TokenType) -> Optional[Token]:
        token = self.peek()
        if token and token.token in tokens:
            return self.advance()
        return None


def _primary(parser: _ParseView) -> Expr:
    if parser.match(TokenType.TRUE):
        return Literal(True)
    if parser.match(TokenType.FALSE):
        return Literal(False)
    if parser.match(TokenType.NIL):
        return Literal(None)
    if token := parser.match(TokenType.NUMBER, TokenType.STRING):
        return Literal(token.literal)
    if start := parser.match(TokenType.LEFT_PAREN):
        expr = _expression(parser)
        if parser.match(TokenType.RIGHT_PAREN):
            return Grouping(expr)
        else:
            error(start.line, "Unterminated grouping")


def _unary(parser: _ParseView) -> Expr:
    if operator := parser.match(TokenType.BANG, TokenType.MINUS):
        right = _unary(parser)
        return Unary(operator, right)

    return _primary(parser)


def _factor(parser: _ParseView) -> Expr:
    expr = _unary(parser)

    while operator := parser.match(TokenType.SLASH, TokenType.STAR):
        right = _unary(parser)
        expr = Binary(expr, operator, right)

    return expr


def _term(parser: _ParseView) -> Expr:
    expr = _factor(parser)

    while operator := parser.match(TokenType.PLUS, TokenType.MINUS):
        right = _factor(parser)
        expr = Binary(expr, operator, right)

    return expr


def _comparison(parser: _ParseView) -> Expr:
    expr = _term(parser)

    while operator := parser.match(
        TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL
    ):
        right = _term(parser)
        expr = Binary(expr, operator, right)

    return expr


def _equality(parser: _ParseView) -> Expr:
    expr = _comparison(parser)

    while operator := parser.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
        right = _comparison(parser)
        expr = Binary(expr, operator, right)

    return expr


def _expression(parser: _ParseView) -> Expr:
    return _equality(parser)


def parse(tokens: Iterable[Token]) -> Expr:
    return _expression(_ParseView(tokens))
