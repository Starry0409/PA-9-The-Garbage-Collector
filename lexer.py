
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    lexeme: str
    line: int


class LexError(Exception):
    pass


_MASTER_RE = re.compile(
    r"(?P<WHITESPACE>\s+)"
    r"|(?P<COMMENT>\#[^\n]*)"
    r"|(?P<NUMBER>\d+)"
    r"|(?P<IDENT>[A-Za-z_]\w*)"
    r"|(?P<PLUS>\+)"
    r"|(?P<MINUS>-)"
    r"|(?P<STAR>\*)"
    r"|(?P<SLASH>/)"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<ASSIGN>=)"
    r"|(?P<SEMI>;)"
)


def tokenize(source: str) -> List[Token]:
    tokens = []
    line = 1
    pos = 0

    while pos < len(source):
        match = _MASTER_RE.match(source, pos)

        if match is None:
            raise LexError(
                f"Unexpected character '{source[pos]}' on line {line}"
            )

        kind = match.lastgroup
        value = match.group()

        if kind not in ("WHITESPACE", "COMMENT"):
            if kind == "IDENT" and value == "let":
                kind = "LET"

            tokens.append(Token(kind, value, line))

        line += value.count("\n")
        pos = match.end()

    tokens.append(Token("EOF", "", line))
    return tokens
