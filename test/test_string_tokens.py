# -*- coding: utf-8 -*-
"""
Tests translation from text characters to the token: String
"""

from typing import Optional

import pytest

from mathics_scanner.errors import EscapeSyntaxError, IncompleteSyntaxError
from mathics_scanner.feed import SingleLineFeeder
from mathics_scanner.location import ContainerKind
from mathics_scanner.tokeniser import Token, Tokeniser


def check_string(
    source_text,
    expected_text: str,
    message: Optional[str] = "",
    expected_tag: Optional[str] = None,
):
    token = single_token(source_text)
    assert token is not None

    if expected_tag is None:
        expected_tag = "String"
    assert token.tag == expected_tag

    if message:
        assert token.text == expected_text, message
    else:
        assert token.text == expected_text


def incomplete_error(s: str, failure_msg: str):
    with pytest.raises(IncompleteSyntaxError) as excinfo:
        get_tokens(s)

    assert excinfo, failure_msg


def escape_scan_error(s: str, failure_msg: str):
    with pytest.raises(EscapeSyntaxError) as excinfo:
        get_tokens(s)

    assert excinfo, failure_msg


def single_token(source_text: str) -> Token:
    tokens = get_tokens(source_text)
    assert len(tokens) == 1
    token = tokens[0]
    return token


def get_tokens(source_text: str):
    tokeniser = Tokeniser(
        SingleLineFeeder(source_text, "<get_tokens>", ContainerKind.STRING)
    )
    tokens = []
    while True:
        token = tokeniser.next()
        if token.tag == "END":
            break
        else:
            tokens.append(token)
    return tokens


def test_string():
    # Plain strings
    check_string('""', '""', "Null string")
    check_string('"abc"', '"abc"', "Simple sequence")

    # Number conversions for binary, octal, hexadecimal
    check_string(r'"a\\b"', r'"a\b"', "escaped backslash in a string")
    check_string(r'"\102"', '"B"', "Octal number test in a string")
    check_string(r'"q\.b4"', '"q´"', "2-digit hexadecimal number in a string")

    check_string(r'"\\c"', '"\\c"', "escaped backslash at beginning of string")

    # All valid ASCII-like control escape sequences
    for escape_string in ("\b", "\f", "\n", "\r", "\t"):
        check_string(f'"a{escape_string}"', f'"a{escape_string}"')

    check_string(r'"\ abc"', '" abc"', "Escaped space in a string is valid")
    check_string(r'"abc(*def*)"', r'"abc(*def*)"')

    # Example found in usage string for FCSetPauliSigmaScheme of
    # FeynCalc.
    check_string(
        r'"$\{\\sigma^i, \\sigma^j \}$."',
        r'"$\{\sigma^i, \sigma^j \}$."',
        "Escaped braces inside a string are ok",
    )

    check_string(
        r'"\(a \+\)"',
        r'"\(a \+\)"',
        "Do not interpret, but preserve boxing inside a string",
    )

    incomplete_error(r'"abc', "String does not have terminating quote")
    incomplete_error(r'"\"', "Unterminated escape sequence")

    escape_scan_error(r'"a\g"', "Unknown string escape \\g")
    escape_scan_error(r'"a\X"', '"X" is not a valid escape character')


# https://www.wolfram.com/language/12/networking-and-system-operations/use-the-full-range-of-unicode-characters.html
# describes hex encoding.


def test_octal():
    check_string(r'"a\050"', r'"a("', "Octal '(' in string")
    check_string(r'"a\051"', r'"a)"', "Octal ')' in string")
    check_string(r'"a\052"', r'"a*"', "Octal '*' in string")


def test_hexadecimal_dot():
    check_string(r'"\.30"', '"0"', "2-digit hexadecimal ASCII number 0")
    check_string(r'"\.42"', '"B"', "2-digit hexadecimal ASCII capital B")
    check_string(
        r"\.42\.30",
        "B0",
        "hexademimal encoding of identifier in expression context",
        "Symbol",
    )


def test_hexadecimal_colon():
    check_string(
        r'"\:03B8"',
        '"θ"',
        "4-digit hexadecimal number test with uppercase alpha letter",
    )
    check_string(r'"\:0030"', '"0"')
    check_string(
        r"\:03b8",
        "\u03b8",
        "4-digit hexadecimal number test with lowercase alpha letter",
        "Symbol",
    )


def test_hexadecimal_vbar():
    check_string(r'"\|01D451"', '"\U0001d451"')
