from typing import Iterable, List, Tuple

from pylox.error import error
from pylox.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Lambda,
    Logical,
    Super,
    This,
    Unary,
    Literal,
    Variable,
    Set,
)
from pylox.scanner import Token, TokenType
from pylox.stmt import Block, Class, ExprStmt, Fun, If, Print, Return, Stmt, Var, While


class ParseError(Exception):
    pass


class _ParseView:
    def __init__(self, tokens: Iterable[Token]):
        self._tokens = list(tokens)
        self._current = 0

    def is_at_end(self) -> bool:
        return self._current >= len(self._tokens)

    def peek(self) -> Token | None:
        if self.is_at_end():
            return None
        return self._tokens[self._current]

    def check(self, expected: TokenType) -> Token | None:
        token = self.peek()
        if token and token.token == expected:
            return token
        return None

    def check_ahead(self, n: int, expected: TokenType) -> Token | None:
        i = self._current + n
        if i <= len(self._tokens) and self._tokens[i].token == expected:
            return self._tokens[i]
        return None

    def advance(self) -> Token:
        val = self.peek()
        self._current += 1
        return val

    def match(self, *tokens: TokenType) -> Token | None:
        token = self.peek()
        if token and token.token in tokens:
            return self.advance()
        return None

    def _error(self, token: Token, message: str) -> ParseError:
        error(token.line, message)
        return ParseError()

    def consume(self, expected: TokenType, message: str) -> Token:
        token = self.peek()
        if token and token.token == expected:
            return self.advance()

        raise self._error(token or self._tokens[-1], message)


def _primary(parser: _ParseView) -> Expr:
    if parser.match(TokenType.TRUE):
        return Literal(True)
    if parser.match(TokenType.FALSE):
        return Literal(False)
    if token := parser.match(TokenType.THIS):
        return This(token)
    if token := parser.match(TokenType.SUPER):
        parser.consume(TokenType.DOT, "Expect '.' after super expression.")
        method = parser.consume(TokenType.IDENTIFIER, "Expect super class method name")
        return Super(token, method)
    if parser.match(TokenType.NIL):
        return Literal(None)
    if token := parser.match(TokenType.NUMBER, TokenType.STRING):
        return Literal(token.literal)
    if parser.match(TokenType.LEFT_PAREN):
        expr = _expression(parser)
        parser.consume(TokenType.RIGHT_PAREN, "Unterminated grouping")
        return Grouping(expr)
    if identifier := parser.match(TokenType.IDENTIFIER):
        return Variable(identifier)
    if fun := parser.match(TokenType.FUN):
        params, body = _parse_fun_defn(parser)
        return Lambda(fun, params, body)


def _finish_call(parser: _ParseView, callee: Expr):
    args: List[Expr] = []
    if not parser.check(TokenType.RIGHT_PAREN):
        while True:
            args.append(_expression(parser))
            if parser.check(TokenType.RIGHT_PAREN):
                break
            parser.consume(TokenType.COMMA, "Expected ','.")

    return Call(callee, args, parser.consume(TokenType.RIGHT_PAREN, "Expected ')'."))


def _call(parser: _ParseView) -> Expr:
    expr = _primary(parser)

    while True:
        if parser.match(TokenType.LEFT_PAREN):
            expr = _finish_call(parser, expr)
        elif parser.match(TokenType.DOT):
            name = parser.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
            expr = Get(expr, name)
        else:
            break

    return expr


def _unary(parser: _ParseView) -> Expr:
    if operator := parser.match(TokenType.BANG, TokenType.MINUS):
        right = _unary(parser)
        return Unary(operator, right)

    return _call(parser)


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


def _and(parser: _ParseView) -> Expr:
    expr = _equality(parser)

    while operator := parser.match(TokenType.AND):
        right = _equality(parser)
        expr = Logical(expr, operator, right)

    return expr


def _or(parser: _ParseView) -> Expr:
    expr = _and(parser)

    while operator := parser.match(TokenType.OR):
        right = _and(parser)
        expr = Logical(expr, operator, right)

    return expr


def _assignment(parser: _ParseView) -> Expr:
    expr = _or(parser)

    if equals := parser.match(TokenType.EQUAL):
        value = _assignment(parser)

        if isinstance(expr, Variable):
            return Assign(expr.name, value)
        elif isinstance(expr, Get):
            return Set(expr.object, expr.name, value)

        parser._error(equals, "Invalid assignment target")

    return expr


def _expression(parser: _ParseView) -> Expr:
    return _assignment(parser)


def _block(parser: _ParseView) -> Iterable[Stmt]:
    while not (parser.is_at_end() or parser.peek().token == TokenType.RIGHT_BRACE):
        yield _declaration(parser)


def _print(parser: _ParseView) -> Print:
    expr = _expression(parser)
    parser.consume(TokenType.SEMICOLON, "Expect ';' after value.")
    return Print(expr)


def _var_decl(parser: _ParseView) -> Var:
    name = parser.consume(TokenType.IDENTIFIER, "Expect variable name.")

    initializer = None
    if parser.match(TokenType.EQUAL):
        initializer = _expression(parser)

    parser.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
    return Var(name, initializer)


def _if(parser: _ParseView) -> If:
    parser.consume(TokenType.LEFT_PAREN, "Expect opening '('.")
    condition = _expression(parser)
    parser.consume(TokenType.RIGHT_PAREN, "Expect closing ')'.")
    if_case = _statement(parser)
    else_case = _statement(parser) if parser.match(TokenType.ELSE) else None
    return If(condition, if_case, else_case)


def _while(parser: _ParseView) -> While:
    parser.consume(TokenType.LEFT_PAREN, "Expect opening '('.")
    condition = _expression(parser)
    parser.consume(TokenType.RIGHT_PAREN, "Expected closing ')'.")
    body = _statement(parser)
    return While(condition, body)


def _for(parser: _ParseView) -> Stmt:
    parser.consume(TokenType.LEFT_PAREN, "Expected opening '('.")
    initializer = None
    if parser.match(TokenType.SEMICOLON):
        initializer = None
    elif parser.match(TokenType.VAR):
        initializer = _var_decl(parser)
    else:
        initializer = _expr_stmt(parser)

    condition = None if parser.check(TokenType.SEMICOLON) else _expression(parser)
    parser.consume(TokenType.SEMICOLON, "Expected ';'.")
    increment = None if parser.check(TokenType.RIGHT_PAREN) else _expression(parser)
    parser.consume(TokenType.RIGHT_PAREN, "Expected closing ')'.")

    body = _statement(parser)

    if increment:
        body = Block([body, increment])

    loop = While(condition or Literal(True), body)

    if initializer:
        loop = Block([initializer, loop])

    return loop


def _parse_fun_defn(parser: _ParseView) -> Tuple[List[Token], List[Stmt]]:
    parser.consume(TokenType.LEFT_PAREN, "Expected '('.")
    params: List[Token] = []
    if not parser.check(TokenType.RIGHT_PAREN):
        while True:
            params.append(parser.consume(TokenType.IDENTIFIER, "Expected identifier."))
            if parser.check(TokenType.RIGHT_PAREN):
                break
            parser.consume(TokenType.COMMA, "Expected ','.")

    parser.consume(TokenType.RIGHT_PAREN, "Expected ')'.")
    parser.consume(TokenType.LEFT_BRACE, "Expected '{'.")
    body = list(_block(parser))
    parser.consume(TokenType.RIGHT_BRACE, "Expected '}'.")

    return params, body


def _fun(parser: _ParseView) -> Fun:
    name = parser.consume(TokenType.IDENTIFIER, "Expected function name.")
    params, body = _parse_fun_defn(parser)
    return Fun(name, params, body)


def _class_decl(parser: _ParseView) -> Class:
    name = parser.consume(TokenType.IDENTIFIER, "Expected class name.")
    superclass = None
    if parser.match(TokenType.LESS):
        super_token = parser.consume(TokenType.IDENTIFIER, "Expected super class identifier.")
        superclass = Variable(super_token)

    parser.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

    methods: List[Fun] = []
    while not parser.check(TokenType.RIGHT_BRACE):
        methods.append(_fun(parser))

    parser.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

    return Class(name, superclass, methods)


def _return(parser: _ParseView, keyword: Token) -> Return:
    expr = None if parser.check(TokenType.SEMICOLON) else _expression(parser)
    return Return(keyword, expr)


def _expr_stmt(parser: _ParseView) -> ExprStmt:
    expr = _expression(parser)
    parser.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
    return ExprStmt(expr)


def _statement(parser: _ParseView) -> Stmt:
    if parser.match(TokenType.PRINT):
        return _print(parser)

    if parser.match(TokenType.LEFT_BRACE):
        stmts = list(_block(parser))
        parser.consume(TokenType.RIGHT_BRACE, "Expect closing '}'.")
        return Block(stmts)

    if parser.match(TokenType.IF):
        return _if(parser)

    if parser.match(TokenType.WHILE):
        return _while(parser)

    if parser.match(TokenType.FOR):
        return _for(parser)

    if keyword := parser.match(TokenType.RETURN):
        return _return(parser, keyword)

    return _expr_stmt(parser)


def _declaration(parser: _ParseView) -> Stmt:
    if parser.match(TokenType.CLASS):
        return _class_decl(parser)
    if parser.check_ahead(1, TokenType.IDENTIFIER) and parser.match(TokenType.FUN):
        return _fun(parser)

    if parser.match(TokenType.VAR):
        return _var_decl(parser)

    return _statement(parser)


def parse_expr(tokens: Iterable[Token]) -> object:
    return _expression(_ParseView(tokens))


def parse(tokens: Iterable[Token]) -> Iterable[Stmt]:
    parser = _ParseView(tokens)

    try:
        while not parser.is_at_end():
            yield _declaration(parser)
    except ParseError:
        pass
