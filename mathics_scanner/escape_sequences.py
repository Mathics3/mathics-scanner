"""
Helper Module for tokenizing character escape sequences.
"""

from typing import Optional, Tuple

from mathics_scanner.characters import named_characters
from mathics_scanner.errors import (
    EscapeSyntaxError,
    NamedCharacterSyntaxError,
    ScanError,
)


def parse_base(source_text: str, start_shift: int, end_shift: int, base: int) -> str:
    r"""
    See if characters start_shift .. end shift
    can be converted to an integer in base  ``base``.

    If so, chr(integer value converted from base).

    However, if the conversion fails, then error messages are
    issued and nothing is updated
    """
    start, end = start_shift, end_shift
    result = None
    if end <= len(source_text):
        text = source_text[start:end]
        try:
            result = int(text, base)
        except ValueError:
            pass  # result remains None
    if result is None:
        last = end - start
        if last == 2:
            tag = "sntoct2"
        elif last == 3:
            tag = "sntoct1"
        elif last == 4:
            tag = "snthex"
        else:
            raise ValueError()
        raise ScanError(tag, source_text[start_shift:].rstrip("\n"))

    return chr(result)


def parse_named_character(
    source_text: str, pos: int, start_shift: int
) -> Optional[str]:
    r"""Before calling we have matched "\[".  Scan to the remaining "]" and
    try to match what is found in-between with a known named
    character, e.g. "Theta".  If we can match this, we store
    the unicode character equivalent in ``line_fragments``.
    If we can't find a named character, error messages are
    issued and we leave ``line_fragments`` untouched.
    """
    named_character = source_text[pos + start_shift : pos + start_shift]
    if named_character.isalpha():
        char = named_characters.get(named_character)
        if char is None:
            raise NamedCharacterSyntaxError("sntufn", named_character)
        else:
            return named_character


def parse_escape_sequence(source_text: str, pos: int) -> Tuple[str, int]:
    """
    Given some source text `source_text` at position `pos`, return the escape sequence and the
    follow-on position.
    """
    result = ""
    c = source_text[pos]
    if c == "\\":
        return "\\", pos + 1

    # https://www.wolfram.com/language/12/networking-and-system-operations/use-the-full-range-of-unicode-characters.html
    # describes hex encoding.
    if c == ".":
        # See if we have a 2-digit hexadecimal number.
        # For example, \.42 is "B"
        result += parse_base(source_text, pos + 1, pos + 3, 16)
        pos += 3
    elif c == ":":
        # See if we have a 4-digit hexadecimal number.
        # For example, \:03B8" is Unicode small leter theta: θ.
        result += parse_base(source_text, pos + 1, pos + 5, 16)
        pos += 5
    elif c == "|":
        # See if we have a 6-digit hexadecimal number.
        result += parse_base(source_text, pos + 1, pos + 7, 16)
        pos += 7
    elif c == "[":
        named_character = parse_named_character(source_text, pos, 2)
        if named_character is not None:
            result += named_character
            pos += 4  # ???
    elif c in "01234567":
        # See if we have a 3-digit octal number.
        # For example \065 = "5"
        result += parse_base(source_text, pos, pos + 3, 8)
        pos += 3

    # WMA escape characters \n, \t, \b, \r.
    # Note that these are a similer to Python, but are different.
    # In particular, Python defines "\a" to be ^G (control G),
    # but in WMA, this is invalid.
    elif c in "ntbfr":
        if c == "n":
            result += "\n"
        elif c == "t":
            result += "\t"
        elif c == "b":
            result += "\b"
        elif c == "f":
            result += "\f"
        else:
            assert c == "r"
            result += "\r"
        pos += 1
    elif c in '!"':
        result += c
        pos += 1
    else:
        raise EscapeSyntaxError("Syntax", "stresc" rf"\{c}.")
    return result, pos
