# -*- coding: utf-8 -*-
"""
Tests translation from strings to sequences of tokens.
"""

import random
import sys
from typing import List

import pytest

from mathics_scanner.errors import IncompleteSyntaxError, InvalidSyntaxError, ScanError
from mathics_scanner.feed import SingleLineFeeder
from mathics_scanner.tokeniser import Token, Tokeniser, is_symbol_name

# Helper functions


def check_Number(mathics3_code: str):
    token = single_token(mathics3_code)
    assert token, Token("Number", mathics3_code, 0)


def check_String(mathics3_code: str):
    token = single_token(mathics3_code)
    assert token, Token("String", mathics3_code, 0)


def check_Symbol(mathics3_code: str):
    token = single_token(mathics3_code)
    assert token, Token("Symbol", mathics3_code, 0)


def get_mathics3_tokens(mathics3_code: str) -> List[Token]:
    """
    Returns the sequence of tokesnall of the tokens A generator that returns the next token in string mathics3_code.
    """
    tokenizer = Tokeniser(SingleLineFeeder(mathics3_code))
    mathics3_tokens = list(mathics3_token_generator(tokenizer))
    assert len(mathics3_tokens) > 0
    assert mathics3_tokens[-1].tag == "END"
    return mathics3_tokens[:-1]


def incomplete_error(string):
    with pytest.raises(IncompleteSyntaxError):
        get_mathics3_tokens(string)


def invalid_error(string):
    with pytest.raises(InvalidSyntaxError):
        get_mathics3_tokens(string)


def mathics3_token_generator(tokenizer):
    """
    A generator that returns the next token in string mathics3_code.
    """
    while True:
        token = tokenizer.next()
        if token.tag == "END":
            yield token
            break
        yield token
    return


def scan_error(string):
    with pytest.raises(ScanError):
        get_mathics3_tokens(string)


def single_token(mathics3_code: str):
    toks = get_mathics3_tokens(mathics3_code)
    assert len(toks) == 1
    token = toks[0]
    return token


def tags(mathics3_code: str):
    return [token.tag for token in get_mathics3_tokens(mathics3_code)]


# Testing starts here...


def test_accuracy():
    scan_error("1.5``")
    check_Number("1.0``20")
    check_Number("1.0``0")
    check_Number("1.4``-20")


def test_apply():
    assert get_mathics3_tokens("f // x") == [
        Token("Symbol", "f", 0),
        Token("Postfix", "//", 2),
        Token("Symbol", "x", 5),
    ]
    assert get_mathics3_tokens("f @ x") == [
        Token("Symbol", "f", 0),
        Token("Prefix", "@", 2),
        Token("Symbol", "x", 4),
    ]
    assert get_mathics3_tokens("f ~ x") == [
        Token("Symbol", "f", 0),
        Token("Infix", "~", 2),
        Token("Symbol", "x", 4),
    ]


def test_association():
    assert get_mathics3_tokens("<|x -> m|>") == [
        Token("RawLeftAssociation", "<|", 0),
        Token("Symbol", "x", 2),
        Token("Rule", "->", 4),
        Token("Symbol", "m", 7),
        Token("RawRightAssociation", "|>", 8),
    ]


def test_backslash():
    assert get_mathics3_tokens("\\[Backslash]") == [Token("Backslash", "\u2216", 0)]

    assert get_mathics3_tokens("\\ a") == [
        Token("RawBackslash", "\\", 0),
        Token("Symbol", "a", 2),
    ]

    incomplete_error("\\")


def test_boxes():
    tokenizer = Tokeniser(SingleLineFeeder("\\(1\\)"))
    assert tokenizer.mode == "expr"
    token_generator = mathics3_token_generator(tokenizer)
    for expect_token, expect_mode in (
        (Token("LeftRowBox", r"\(", 0), "box_expr"),
        (Token("Number", "1", 2), "box_expr"),
        (Token("RightRowBox", r"\)", 3), "expr"),
    ):
        token = next(token_generator)
        assert token == expect_token
        assert tokenizer.mode == expect_mode

    tokenizer = Tokeniser(SingleLineFeeder(r"""\( x \(n \& 2 \) \)"""))
    assert tokenizer.mode == "expr"
    token_generator = mathics3_token_generator(tokenizer)

    for expect_token, expect_mode in (
        (Token("LeftRowBox", r"\(", 0), "box_expr"),
        (Token("Symbol", "x", 3), "box_expr"),
        (Token("LeftRowBox", r"\(", 5), "box_expr"),
        (Token("Symbol", "n", 7), "box_expr"),
        (Token("OverscriptBox", r"\&", 9), "box_expr"),
        (Token("Number", "2", 12), "box_expr"),
        (Token("RightRowBox", r"\)", 14), "box_expr"),
        (Token("RightRowBox", r"\)", 17), "expr"),
    ):
        token = next(token_generator)
        assert token == expect_token
        assert tokenizer.mode == expect_mode


def test_information():
    assert get_mathics3_tokens("??Sin") == [
        Token("Information", "??", 0),
        Token("Symbol", "Sin", 2),
    ]

    assert get_mathics3_tokens("? ?Sin") == [
        Token("PatternTest", "?", 0),
        Token("PatternTest", "?", 2),
        Token("Symbol", "Sin", 3),
    ]


def test_int_repeated():
    assert get_mathics3_tokens("1..") == [
        Token("Number", "1", 0),
        Token("Repeated", "..", 1),
    ]
    assert get_mathics3_tokens("1. .") == [
        Token("Number", "1.", 0),
        Token("Dot", ".", 3),
    ]


def test_integeral():
    assert get_mathics3_tokens("\u222B x \uf74c y") == [
        Token("Integral", "\u222B", 0),
        Token("Symbol", "x", 2),
        Token("DifferentialD", "\uf74c", 4),
        Token("Symbol", "y", 6),
    ]


def test_is_symbol():
    assert is_symbol_name("Derivative")
    assert not is_symbol_name("98")  # symbols can't start with numbers


def test_Filename():
    """
    Test that we can parse file names, and that we get into and out of
    "filename" parsing mode.
    """
    filename = "test_file.m"
    for operator, operator_name in (("<<", "Get"), (">>", "Put"), (">>>", "PutAppend")):
        tokenizer = Tokeniser(SingleLineFeeder(f"{operator} {filename}"))
        assert tokenizer.mode == "expr"
        token_generator = mathics3_token_generator(tokenizer)
        for expect_token, expect_mode in (
            (Token(operator_name, operator, 0), "filename"),
            (Token("Filename", filename, len(operator) + 1), "expr"),
        ):
            token = next(token_generator)
            assert token == expect_token
            assert tokenizer.mode == expect_mode


def test_function():
    assert get_mathics3_tokens("x&") == [
        Token("Symbol", "x", 0),
        Token("Function", "&", 1),
    ]
    assert get_mathics3_tokens("x\uf4a1") == [
        Token("Symbol", "x", 0),
        Token("Function", "\uf4a1", 1),
    ]


def test_Number():
    assert tags("1.5") == ["Number"]
    assert tags("1.5*^10") == ["Number"]
    check_Number("0")


def test_number_base():
    check_Number("8^^23")
    check_Number("10*^3")
    check_Number("10*^-3")
    check_Number("8^^23*^2")


def test_number_big():
    for _ in range(10):
        check_Number(str(random.randint(0, sys.maxsize)))
        check_Number(str(random.randint(sys.maxsize, sys.maxsize * sys.maxsize)))


def test_number_real():
    check_Number("1.5")
    check_Number("1.5`")
    check_Number("0.0")


def test_pre():
    assert get_mathics3_tokens("++x++") == [
        Token("Increment", "++", 0),
        Token("Symbol", "x", 2),
        Token("Increment", "++", 3),
    ]


def test_precision():
    check_Number("1.5`-5")
    check_Number("1.5`0")
    check_Number("1.5`10")


def test_String():
    check_String(r'"abc"')
    incomplete_error(r'"abc')
    check_String(r'"abc(*def*)"')
    check_String(r'"a\"b\\c"')
    incomplete_error(r'"\"')


def test_set():
    assert get_mathics3_tokens("x = y") == [
        Token("Symbol", "x", 0),
        Token("Set", "=", 2),
        Token("Symbol", "y", 4),
    ]
    assert get_mathics3_tokens("x /: y = z") == [
        Token("Symbol", "x", 0),
        Token("TagSet", "/:", 2),
        Token("Symbol", "y", 5),
        Token("Set", "=", 7),
        Token("Symbol", "z", 9),
    ]


def test_symbol():
    check_Symbol("xX")
    check_Symbol("context`name")
    check_Symbol("`name")
    check_Symbol("`context`name")


def test_unset():
    assert get_mathics3_tokens("=.") == [Token("Unset", "=.", 0)]

    assert get_mathics3_tokens("= .") == [Token("Unset", "= .", 0)]
    assert get_mathics3_tokens("=.5") == [
        Token("Set", "=", 0),
        Token("Number", ".5", 1),
    ]
    assert get_mathics3_tokens("= ..") == [
        Token("Set", "=", 0),
        Token("Repeated", "..", 2),
    ]
