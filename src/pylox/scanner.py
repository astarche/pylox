from enum import Enum, auto
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from pylox.error import error


class TokenType(Enum):
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    STAR = auto()
    SLASH = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    EOF = auto()


KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


@dataclass(slots=True, eq=True, frozen=True)
class Token:
    token: TokenType
    lexeme: str
    literal: object
    line: int
    index: int


class _ScanView:
    def __init__(self, input: str):
        self._input = input
        self.start = 0
        self._current = 0
        self.line = 1

    def is_at_end(self) -> bool:
        return self._current >= len(self._input)

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self._input[self._current]

    def peek_next(self) -> str:
        next_index = self._current + 1
        if next_index >= len(self._input):
            return "\0"
        return self._input[next_index]

    def advance(self) -> str:
        val = self.peek()
        if val == "\n":
            self.line += 1
        self._current += 1
        return val

    def advance_while(self, pred: Callable[[str], bool]) -> None:
        while not self.is_at_end() and pred(self.peek()):
            self.advance()

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def start_token(self) -> None:
        self.start = self._current

    @property
    def token(self) -> str:
        return self._input[self.start : self._current]


def _is_digit(val: str):
    return "0" <= val <= "9"


def _is_alpha(val: str):
    return "A" <= val <= "Z" or "a" <= val <= "z" or val == "_"


def _is_alpha_numeric(val: str):
    return _is_alpha(val) or _is_digit(val)


def scan_tokens(input: str) -> Iterable[Token]:
    scan = _ScanView(input)

    def create_token(type, literal=None) -> Token:
        return Token(type, scan.token, literal, scan.line, scan.start)

    while not scan.is_at_end():
        scan.start_token()
        match scan.advance():
            case "(":
                yield create_token(TokenType.LEFT_PAREN)
            case ")":
                yield create_token(TokenType.RIGHT_PAREN)
            case "{":
                yield create_token(TokenType.LEFT_BRACE)
            case "}":
                yield create_token(TokenType.RIGHT_BRACE)
            case ",":
                yield create_token(TokenType.COMMA)
            case ".":
                yield create_token(TokenType.DOT)
            case "+":
                yield create_token(TokenType.PLUS)
            case "-":
                yield create_token(TokenType.MINUS)
            case ";":
                yield create_token(TokenType.SEMICOLON)
            case "*":
                yield create_token(TokenType.STAR)
            case "/":
                if scan.peek() == "/":
                    scan.advance_while(lambda s: s != "\n")
                else:
                    yield create_token(TokenType.SLASH)
            case "=":
                yield create_token(TokenType.EQUAL_EQUAL if scan.match("=") else TokenType.EQUAL)
            case ">":
                yield create_token(
                    TokenType.GREATER_EQUAL if scan.match("=") else TokenType.GREATER
                )
            case "<":
                yield create_token(TokenType.LESS_EQUAL if scan.match("=") else TokenType.LESS)
            case "!":
                yield create_token(TokenType.BANG_EQUAL if scan.match("=") else TokenType.BANG)
            case '"':
                scan.advance_while(lambda s: s != '"')
                if scan.match('"'):
                    yield create_token(TokenType.STRING, scan.token[1:-1])
                else:
                    error(scan.line, f"Unterminated string {scan.token}")
                    break
            case " " | "\t" | "\r" | "\n":
                pass
            case _ as token:
                if _is_digit(token):
                    scan.advance_while(_is_digit)
                    if scan.peek() == "." and _is_digit(scan.peek_next()):
                        scan.advance()
                        scan.advance_while(_is_digit)
                    yield create_token(TokenType.NUMBER, float(scan.token))
                elif _is_alpha(token):
                    scan.advance_while(_is_alpha_numeric)
                    token_type = KEYWORDS.get(scan.token, TokenType.IDENTIFIER)
                    yield create_token(token_type)
                else:
                    error(scan.line, f"Unexpected token {token}")
