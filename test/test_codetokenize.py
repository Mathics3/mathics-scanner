# -*- coding: utf-8 -*-
"""
Tests translation from strings to sequences of tokens in CodeTokenize format.
"""

from typing import List

from mathics_scanner.feed import SingleLineFeeder
from mathics_scanner.tokeniser import Token, Tokeniser


def tokens(code: str) -> List[Token]:
    tokeniser = Tokeniser(SingleLineFeeder(code))
    tokens = []
    while True:
        token = tokeniser.next()
        if token.tag == "END":
            break
        else:
            tokens.append(token)
    return [token.code_tokenize_format for token in tokens]


def test_CodeTokenize():
    for input_str, expected in (
        ("5!", ["LeafNode[Token`Number, '5', 0]", "LeafNode[Token`Bang, '!', 1]"]),
        (
            "6!!",
            ["LeafNode[Token`Number, '6', 0]", "LeafNode[Token`BangBang, '!!', 1]"],
        ),
        (
            "?Plus",
            ["LeafNode[Token`Question, '?', 0]", "LeafNode[Symbol, 'Plus', 1]"],
        ),
        (
            "??Times",
            [
                "LeafNode[Token`QuesionQuestion, '??', 0]",
                "LeafNode[Symbol, 'Times', 2]",
            ],
        ),
        (
            "x--",
            [
                "LeafNode[Symbol, 'x', 0]",
                "LeafNode[Token`MinusMinus, '--', 1]",
            ],
        ),
        (
            "x!",
            [
                "LeafNode[Symbol, 'x', 0]",
                "LeafNode[Token`Bang, '!', 1]",
            ],
        ),
        (
            "x!!",
            [
                "LeafNode[Symbol, 'x', 0]",
                "LeafNode[Token`BangBang, '!!', 1]",
            ],
        ),
        (
            "a > b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Greater, '>', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a < b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Less, '<', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a >> b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`GreaterGreater, '>>', 2]",
                "LeafNode[Token`Filename, 'b', 5]",
            ],
        ),
        (
            "a << b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`LessLess, '<<', 2]",
                "LeafNode[Token`Filename, 'b', 5]",
            ],
        ),
        (
            "a >= b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`GreaterEqual, '>=', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a <= b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`LessEqual, '<=', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a + b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Plus, '+', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a | b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Bar, '|', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a || b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`BarBar, '||', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a & b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Amp, '&', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a && b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`AmpAmp, '&&', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a / b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Slash, '/', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a /. b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`SlashDot, '/.', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a // b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`SlashSlash, '//', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a //. b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`SlashSlashDot, '//.', 2]",
                "LeafNode[Symbol, 'b', 6]",
            ],
        ),
        (
            "a = b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`Equal, '=', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a == b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`EqualEqual, '==', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a === b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`EqualEqualEqual, '===', 2]",
                "LeafNode[Symbol, 'b', 6]",
            ],
        ),
        (
            "a += b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`PlusEqual, '+=', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a -= b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`MinusEqual, '-=', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a *= b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`StarEqual, '*=', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a /= b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`SlashEqual, '/=', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a @ b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`At, '@', 2]",
                "LeafNode[Symbol, 'b', 4]",
            ],
        ),
        (
            "a @@ b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`AtAt, '@@', 2]",
                "LeafNode[Symbol, 'b', 5]",
            ],
        ),
        (
            "a @@@ b",
            [
                "LeafNode[Symbol, 'a', 0]",
                "LeafNode[Token`AtAtAt, '@@@', 2]",
                "LeafNode[Symbol, 'b', 6]",
            ],
        ),
    ):
        assert tokens(input_str) == expected
