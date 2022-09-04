# -*- coding: utf-8 -*-
import pytest

from mathics_scanner import IncompleteSyntaxError, ScanError
from mathics_scanner.prescanner import Prescanner
from mathics_scanner.feed import SingleLineFeeder


def replace_escape_sequences(code):
    prescanner = Prescanner(SingleLineFeeder(code))
    return prescanner.replace_escape_sequences()


def invalid(code):
    with pytest.raises(ScanError):
        replace_escape_sequences(code)


def incomplete(code):
    with pytest.raises(IncompleteSyntaxError):
        replace_escape_sequences(code)


def equal(code, result):
    assert replace_escape_sequences(code) == result


def equal_length(code, length):
    assert len(replace_escape_sequences(code)) == length


def test_named_characters():
    equal(r"\[Theta]", "\u03B8")
    equal(r"\[CapitalPi]", "\u03A0")
    equal(r"\[Fake]", r"\[Fake]")
    equal("z \\[Conjugate]", "z \uF3C8")
    equal("z \\[Integral]", "z \u222b")
    equal("z \\\\[Integral]", "z \\\\[Integral]")
    equal("z \\\\\\[Integral]", "z \\\\\u222b")
    equal("abc\\\\", "abc\\\\")


def test_text_lengths():
    equal_length(r'"\[Integral]"', 3)
    # Prescanner keep both slashes and quotes.
    # The tokenizer brings \\ into \ if it appears
    # inside a string.
    equal_length(r'"\\[Integral]"', 14)


def test_oct():
    equal(r"\051", ")")


def test_hex_dot():
    equal(r"\.30", "0")


def test_hex_colon():
    equal(r"\:0030", "0")
    equal(r"\:03B8", "\u03B8")
    equal(r"\:03b8", "\u03B8")


def test_hex_vbar():
    equal(r"\|01D451", "\U0001D451")


def test_incomplete():
    incomplete(r"\[")
    incomplete(r"\[Theta")


def test_invalid_oct():
    invalid(r"\093")
    invalid(r"\01")


def test_invalid_colon():
    invalid(r"\:")
    invalid(r"\:A")
    invalid(r"\:01")
    invalid(r"\:A1")
    invalid(r"\:ak")
    invalid(r"\:A10")
    invalid(r"\:a1g")
    invalid(r"\:A1g9")
    invalid(r"\:01-2")


def test_invalid_dot():
    invalid(r"\.")
    invalid(r"\.0")


def test_combined():
    equal(r"\:03B8\[Theta]\.30\052", "\u03B8\u03B80*")


def test_nested():
    equal(r"\[Thet\141]", r"\[Thet\141]")


def test_trailing_backslash():
    incomplete("x \\")
