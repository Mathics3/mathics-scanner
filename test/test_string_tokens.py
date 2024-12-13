# -*- coding: utf-8 -*-
"""
Tests translation from text characters to the token: String
"""

import pytest

from mathics_scanner.errors import IncompleteSyntaxError, ScanError
from mathics_scanner.feed import SingleLineFeeder
from mathics_scanner.tokeniser import Token, Tokeniser


def check_string(source_text, expected_text: str):
    token = single_token(source_text)
    assert token is not None
    assert token.tag == "String"
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
    for escape_string in ("\b", "\f", "\n", "\r", "\t"):
        check_string(f'"a{escape_string}"', f'"a{escape_string}"')

    # Broken:
    # "a\050", "a\051" "a\052"
    # Prescanning eagerly replaces the escape sequences with
    # symbols "(", ")", or "*" respectively and this messes up parsing
    # somehow.
    check_string(r'"abc"', r'"abc"')
    check_string(r'"abc(*def*)"', r'"abc(*def*)"')
    check_string(r'"a\"b\\c"', r'"a\"b\\c"')
    incomplete_error(r'"abc', "String does not have terminating quote")
    incomplete_error(r'"\"', "Unterminated escape sequence")
    # scan_error(r'"a\X"', '"X" is not a valid escape character')
