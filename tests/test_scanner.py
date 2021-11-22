from pylox.scanner import scan_tokens, Token, TokenType


def test_parse_single_char():
    tokens = [t.token for t in scan_tokens("*;(){+}-/")]
    expected = [
        TokenType.STAR,
        TokenType.SEMICOLON,
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE,
        TokenType.PLUS,
        TokenType.RIGHT_BRACE,
        TokenType.MINUS,
        TokenType.SLASH,
    ]

    assert tokens == expected


def test_parse_numbers():
    tokens = [
        t.literal
        for t in scan_tokens("{ 34 } { 123.45 } { 0.0 } { 999 }")
        if t.token == TokenType.NUMBER
    ]
    expected = [34, 123.45, 0.0, 999]

    assert tokens == expected


def test_parse_strings():
    tokens = list(scan_tokens('"Hello" + "World"'))
    expected = [
        Token(TokenType.STRING, '"Hello"', "Hello", 1),
        Token(TokenType.PLUS, "+", None, 1),
        Token(TokenType.STRING, '"World"', "World", 1),
    ]

    assert tokens == expected


def test_parse_identifiers():
    tokens = [t.token for t in scan_tokens("var x = y")]
    expected = [TokenType.VAR, TokenType.IDENTIFIER, TokenType.EQUAL, TokenType.IDENTIFIER]

    assert tokens == expected
