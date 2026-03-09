# -*- coding: utf-8 -*-
"""
Tests regular expressions used in the tokenizer.
"""
import re

from mathics_scanner.tokeniser import (
    FILENAME_PATTERN,
    FULL_SYMBOL_PATTERN_STR,
    FULL_SYMBOL_PATTERN_WITH_NAMES_WILDCARD_RE,
    NUMBER_PATTERN,
    compile_pattern,
)

NUMBER_PATTERN_RE = compile_pattern(NUMBER_PATTERN)
FILENAME_PATTERN_RE = compile_pattern(FILENAME_PATTERN)


def check_pattern(pattern_re: re.Pattern, text: str, pattern_type: str):
    matched = re.match(pattern_re, text)
    assert matched, f"{text} should match as a valid Mathics3 {pattern_type}"
    assert matched.string == text, f"{text} should match entire string unchanged"


def test_numeric_patterns():
    assert isinstance(
        NUMBER_PATTERN_RE, re.Pattern
    ), "NUMBER_PATTERN_RE should have compiled"
    for symbol in ("1", "2.", "3.0``20", "4.0``0", "5.6``-20"):
        check_pattern(NUMBER_PATTERN_RE, symbol, "Number")


def test_filename_patterns():
    for filename in ("foo.m", '"foo.m"', '"foo.wl"', '"/etc/hosts"', r"C:\WINDOWS.SYS"):
        check_pattern(FILENAME_PATTERN_RE, filename, "FileName")

    for filename, fail_msg in (
        ("'foo.m'", "Filename using single quotes is not allowed"),
        ('"foo.m', "File must end with a double quote when it starts with one"),
    ):
        assert re.match(FILENAME_PATTERN_RE, filename) is None, fail_msg


def test_symbol_patterns():
    for symbol in ("xX", "context`name", "`name" "`context`name"):
        check_pattern(FULL_SYMBOL_PATTERN_STR, symbol, "Symbol")
        check_pattern(FULL_SYMBOL_PATTERN_WITH_NAMES_WILDCARD_RE, symbol, "Symbols")


def test_name_patterns():
    for symbol in ("*", "Foo*.wl", "Foo@", '"Bar"'):
        check_pattern(
            FULL_SYMBOL_PATTERN_WITH_NAMES_WILDCARD_RE, symbol, "Names Patterns"
        )
