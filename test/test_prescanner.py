# -*- coding: utf-8 -*-
import pytest

from mathics_scanner import IncompleteSyntaxError, ScanError
from mathics_scanner.feed import SingleLineFeeder
from mathics_scanner.prescanner import Prescanner


def replace_escape_sequences(mathics_text: str):
    prescanner = Prescanner(SingleLineFeeder(mathics_text))
    return prescanner.replace_escape_sequences()


def assert_invalid(mathics_text: str):
    with pytest.raises(ScanError):
        replace_escape_sequences(mathics_text)


def assert_incomplete(mathics_text: str):
    with pytest.raises(IncompleteSyntaxError):
        replace_escape_sequences(mathics_text)


def assert_equal(mathics_text: str, result: str):
    assert replace_escape_sequences(mathics_text) == result


def assert_equal_length(mathics_text: str, length):
    assert len(replace_escape_sequences(mathics_text)) == length


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_named_characters():
    assert_equal(r"\[Theta]", "\u03B8")
    assert_equal(r"\[CapitalPi]", "\u03A0")
    assert_equal(r"\[Fake]", r"\[Fake]")
    assert_equal("z \\[Conjugate]", "z \uF3C8")
    assert_equal("z \\[Integral]", "z \u222b")
    assert_equal("z \\\\[Integral]", "z \\\\[Integral]")
    assert_equal("z \\\\\\[Integral]", "z \\\\\u222b")
    assert_equal("abc\\\\", "abc\\\\")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_text_lengths():
    assert_equal_length(r'"\[Integral]"', 3)
    # Prescanner keep both slashes and quotes.
    # The tokenizer brings \\ into \ if it appears
    # inside a string.
    assert_equal_length(r'"\\[Integral]"', 14)


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_incomplete():
    assert_incomplete(r"\[")
    assert_incomplete(r"\[Theta")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_invalid_octal():
    assert_invalid(r"\093")
    assert_invalid(r"\01")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_invalid_colon():
    assert_invalid(r"\:")
    assert_invalid(r"\:A")
    assert_invalid(r"\:01")
    assert_invalid(r"\:A1")
    assert_invalid(r"\:ak")
    assert_invalid(r"\:A10")
    assert_invalid(r"\:a1g")
    assert_invalid(r"\:A1g9")
    assert_invalid(r"\:01-2")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_invalid_dot():
    assert_invalid(r"\.")
    assert_invalid(r"\.0")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_combined():
    assert_equal(r"\:03B8\[Theta]\.30\052", "\u03B8\u03B80*")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_nested():
    assert_equal(r"\[Thet\141]", r"\[Thet\141]")


@pytest.mark.skip("Prescanner tests need to be integrated outside of prescanner")
def test_trailing_backslash():
    assert_incomplete("x \\")
