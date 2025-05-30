# -*- coding: utf-8 -*-
import pytest

from mathics_scanner.errors import NamedCharacterSyntaxError, SyntaxError
from mathics_scanner.escape_sequences import parse_escape_sequence


def test_escape_sequences():
    for text, pos, expect_pos, expect_str, fail_msg in (
        # Backslash
        ("\\\\", 0, 1, "\\", "backslash"),
        ("abc \\\\", 5, 6, "\\", "backslash at end"),
        ("abc \\\\n", 5, 6, "\\", "backslash in middle"),
        (
            r"\
abc",
            1,
            2,
            "\n",
            "backslashed at end of line",
        ),
        # Octal
        (r"050", 0, 3, chr(0o50), "character at beginning"),
        (r"a\051", 2, 5, chr(0o51), "Octal character in middle"),
        # With dot (2-character hex)
        (r".30", 0, 3, chr(0x30), "two-character hex"),
        (
            r"a\.3115",
            2,
            5,
            chr(0x31),
            "two-character hex in middle with trailing digits",
        ),
        (r"b\.4dXYZ", 2, 5, chr(0x4D), "two-character hex in middle"),
        # With colon (4-character hex)
        (r":0030", 0, 5, "0", "four-character hex"),
        (r":03B5", 0, 5, "\u03B5", "four-character hex unicode uppercase"),
        (r":03B8", 0, 5, "\u03b8", "four-character hex unicode lowercase"),
        # With Vertical bar (6-character hex)
        (r"|01d450", 0, 7, "\U0001D450", "six-character hex unicode lowercase"),
        (r"|01D451", 0, 7, "\U0001D451", "six-character hex unicode uppercase"),
        # Named Characters
        ("[Theta]", 0, 7, "\u03B8", "Named character; full string"),
        ("abcd[CapitalPi]efg", 4, 15, "\u03A0", "Named character; internal"),
        (r"z \[Conjugate]", 3, 14, "\uF3C8", "Named character; at end"),
        ("[Integral]", 0, 10, "\u222b", "Another full-string named-character"),
    ):
        assert parse_escape_sequence(text, pos) == (expect_str, expect_pos), fail_msg


def test_invalid_named_character_sequences():
    for text in (r"\[", r"\[Theta", r"\[Fake]", r"\[abc]"):
        with pytest.raises(NamedCharacterSyntaxError):
            parse_escape_sequence(text, 1)


def test_invalid_number_encoding():
    for text in (
        # Octal
        "093",  # 9 is not in 0-7
        "01",  # need 3 characters
        "01",  # need 3 characters
        # 2-character hex
        ".",
        ".0",
        ".0i",  # i is not in 0-f
        # 4-character hex
        ":",
        ":A",
        ":A1",
        ":ak",
        ":A10",
        ":a1g",
        ":A1g9",
        ":01-2",
    ):
        with pytest.raises(SyntaxError):
            parse_escape_sequence(text, 0)
