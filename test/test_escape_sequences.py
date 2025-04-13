# -*- coding: utf-8 -*-
from mathics_scanner.escape_sequences import parse_escape_sequence


def test_escape_sequences():
    for text, pos, expect_pos, expect_str, fail_msg in (
        # Backslash
        ("\\\\", 0, 1, "\\", "backslash"),
        ("abc \\\\", 5, 6, "\\", "backslash at end"),
        ("abc \\\\n", 5, 6, "\\", "backslash in middle"),
        # Octal
        (r"051", 0, 3, chr(0o51), "character at beginning"),
        (r"a\051", 2, 5, chr(0o51), "Octal character in middle"),
        # With dot
        (r".30", 0, 3, chr(0x30), "two-character hex"),
        (
            r"a\.3015",
            2,
            5,
            chr(0x30),
            "two-character hex in middle with trailing digits",
        ),
        (r"b\.4dXYZ", 2, 5, chr(0x4D), "two-character hex in middle"),
        # With colon
        (r":0030", 0, 5, "0", "four-character hex"),
        (r":03B8", 0, 5, "\u03B8", "four-character hex unicode uppercase"),
        (r":03B8", 0, 5, "\u03b8", "four-character hex unicode lowercase"),
        # With Vertical bar
        (r"|01d451", 0, 7, "\U0001D451", "six-character hex unicode lowercase"),
        (r"|01D451", 0, 7, "\U0001D451", "six-character hex unicode uppercase"),
    ):
        assert parse_escape_sequence(text, pos) == (expect_str, expect_pos), fail_msg
