# -*- coding: utf-8 -*-
"""
Tests translation from text characters to the token: String
"""

from typing import Optional

import pytest

from mathics_scanner.errors import IncompleteSyntaxError, ScanError
from mathics_scanner.feed import SingleLineFeeder
from mathics_scanner.tokeniser import Token, Tokeniser


def check_string(source_text, expected_text: str, message: Optional[str] = ""):
    token = single_token(source_text)
    assert token is not None
    assert token.tag == "String"
    if message:
        assert token.text == expected_text, message
    else:
        assert token.text == expected_text


def incomplete_error(s: str, failure_msg: str):
    with pytest.raises(IncompleteSyntaxError) as excinfo:
        get_tokens(s)

    assert excinfo, failure_msg


def scan_error(s: str, failure_msg: str):
    with pytest.raises(ScanError) as excinfo:
        get_tokens(s)

    assert excinfo, failure_msg


def single_token(source_text) -> Token:
    tokens = get_tokens(source_text)
    assert len(tokens) == 1
    token = tokens[0]
    return token


def get_tokens(source_text: str):
    tokeniser = Tokeniser(SingleLineFeeder(source_text))
    tokens = []
    while True:
        token = tokeniser.next()
        if token.tag == "END":
            break
        else:
            tokens.append(token)
    return tokens


def test_string():
    # Number conversions for binary, octal, hexadecimal
    check_string(r'"\\c"', '"\\c"', "escaped backslash at beginning of string")
    check_string(r'"a\\b"', r'"a\b"', "escaped backslash")
    check_string(r'"\102"', '"B"', "Octal number test")
    check_string(r'"q\.b4"', '"q´"')

    # All valid ASCII-like control escape sequences
    for escape_string in ("\b", "\f", "\n", "\r", "\t"):
        check_string(f'"a{escape_string}"', f'"a{escape_string}"')

    check_string(r'"abc"', r'"abc"')
    check_string(r'"abc(*def*)"', r'"abc(*def*)"')
    # check_string(r'"a\"b\\c"', r'"a\\"b\c"')
    incomplete_error(r'"abc', "String does not have terminating quote")
    incomplete_error(r'"\"', "Unterminated escape sequence")
    scan_error(r'"a\g"', "Unknown string escape \\g")

    scan_error(r'"a\X"', '"X" is not a valid escape character')


# https://www.wolfram.com/language/12/networking-and-system-operations/use-the-full-range-of-unicode-characters.html
# describes hex encoding.


def test_octal():
    check_string(r'"a\050"', r'"a("', "Octal '(' in string")
    check_string(r'"a\051"', r'"a)"', "Octal ')' in string")
    check_string(r'"a\052"', r'"a*"', "Octal '*' in string")
    # FIXME: add tests ouside of string


def test_hexadecimal_dot():
    check_string(r'"\.30"', '"0"', "2-digit hexadecimal ASCII number 0")
    check_string(r'"\.42"', '"B"', "2-digit hexadecimal ASCII capital B")
    # FIXME: add tests ouside of string


def test_hexadecimal_colon():
    check_string(
        r'"\:03B8"',
        '"θ"',
        "4-digit hexadecimal number test with uppercase alpha letter",
    )
    check_string(
        r'"\:03b8"',
        '"\u03B8"',
        "4-digit hexadecimal number test with lowercase alpha lettter",
    )
    check_string(r'"\:0030"', '"0"')
    # FIXME:
    # check_string(r"\:03b8", "\u03B8", "4-digit hexadecimal number test with lowercase alpha lettter")


def test_hexadecimal_vbar():
    check_string(r'"\|01D451"', '"\U0001D451"')
