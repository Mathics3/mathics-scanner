"""
Helper Module for tokenizing character escape sequences.
"""

from typing import Optional, Tuple

from mathics_scanner.characters import named_characters
from mathics_scanner.errors import (
    EscapeSyntaxError,
    NamedCharacterSyntaxError,
    SyntaxError,
)


def parse_base(source_text: str, start_shift: int, end_shift: int, base: int) -> str:
    r"""
    See if characters start_shift .. end shift
    can be converted to an integer in base  ``base``.

    If so, chr(integer value converted from base) is returnd.

    However, if the conversion fails, SyntaxError is raised.
    """
    last = end_shift - start_shift
    if last == 2:
        tag = "sntoct2"
    elif last == 3:
        assert base == 8, "Only octal requires 3 digits"
        tag = "sntoct1"
    elif last in (4, 6):
        tag = "snthex"
    else:
        raise ValueError()

    if end_shift > len(source_text):
        raise SyntaxError("Syntax", tag)

    assert start_shift <= end_shift
    text = source_text[start_shift:end_shift]
    try:
        result = int(text, base)
    except ValueError:
        raise SyntaxError(tag, source_text[start_shift:].rstrip("\n"))

    return chr(result)


def parse_named_character(source_text: str, start: int, finish: int) -> Optional[str]:
    r"""
    Find the unicode-equivalent symbol for a string named character.

    Before calling we have matched the text between "\["  and "]" of the input.

    The name character is thus in source_text[start:finish].

    Match this string with the known named characters,
    e.g. "Theta".  If we can match this, then we return the unicode equivalent from the
    `named_characters` map (which is read in from JSON but stored in a YAML file).

    If we can't find the named character, rasie NamedCharacterSyntaxError.
    """
    named_character = source_text[start:finish]
    if named_character.isalpha():
        char = named_characters.get(named_character)
        if char is None:
            raise NamedCharacterSyntaxError("sntufn", named_character)
        else:
            return char


def parse_escape_sequence(source_text: str, pos: int) -> Tuple[str, int]:
    """Given some source text in `source_text` starting at offset
    `pos`, return the escape-sequence value for this text and the
    follow-on offset position.
    """
    result = ""
    c = source_text[pos]
    if c == "\\":
        return "\\", pos + 1

    # https://www.wolfram.com/language/12/networking-and-system-operations/use-the-full-range-of-unicode-characters.html
    # describes hex encoding.
    if c == ".":
        # see if we have a 2-digit hexadecimal number.
        # for example, \.42 is "b"
        result += parse_base(source_text, pos + 1, pos + 3, 16)
        pos += 3
    elif c == ":":
        # see if we have a 4-digit hexadecimal number.
        # for example, \:03b8" is unicode small leter theta: θ.
        result += parse_base(source_text, pos + 1, pos + 5, 16)
        pos += 5
    elif c == "|":
        # see if we have a 6-digit hexadecimal number.
        result += parse_base(source_text, pos + 1, pos + 7, 16)
        pos += 7
    elif c == "[":
        pos += 1
        i = pos + 1
        while i < len(source_text):
            if source_text[i] == "]":
                break
            i += 1
        if i == len(source_text):
            # Note: named characters do not have \n's in them. (Is this right)?
            # FIXME: decide what to do here.
            raise NamedCharacterSyntaxError("Syntax", "sntufn", source_text[pos:])

        named_character = parse_named_character(source_text, pos, i)
        if named_character is None:
            raise NamedCharacterSyntaxError("Syntax", "sntufn", source_text[pos:i])

        result += named_character
        pos = i + 1
    elif c in "01234567":
        # See if we have a 3-digit octal number.
        # For example \065 = "5"
        result += parse_base(source_text, pos, pos + 3, 8)
        pos += 3

    # WMA escape characters \n, \t, \b, \r.
    # Note that these are a similer to Python, but are different.
    # In particular, Python defines "\a" to be ^G (control G),
    # but in WMA, this is invalid.
    elif c in "ntbfr $\n":
        if c in "n\n":
            result += "\n"
        elif c == " ":
            result += " "
        elif c == "t":
            result += "\t"
        elif c == "b":
            result += "\b"
        elif c == "f":
            result += "\f"
        elif c in '$"':
            # I don't know why \$ is defined, but it is!
            result += rf"\{c}"
        else:
            assert c == "r"
            result += "\r"
        pos += 1
    elif c in '!"':
        result += c
        pos += 1
    else:
        raise EscapeSyntaxError("stresc", rf"\{c}")
    return result, pos
