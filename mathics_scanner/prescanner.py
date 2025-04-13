# -*- coding: utf-8 -*-
"""
Module for "prescanning". Right now this just means replacing
character escape sequences.
"""

from typing import List, Optional, Tuple

from mathics_scanner.characters import named_characters
from mathics_scanner.errors import IncompleteSyntaxError, ScanError
from mathics_scanner.feed import LineFeeder


class Prescanner(object):
    r"""
    A Class for converting escape sequences:
        Character codes to characters:
            \.7A -> z
            \.004a -> J
            \:004a -> J
            \|01D451  -> \U0001D451
            \041 -> !
        Named Characters to Unicode:
            \[Theta] -> \u03B8
        ASCII escape sequence:
            \n -> literal \n

    Trailing backslash characters (\) are reported incomplete.
    """

    def __init__(self, feeder: LineFeeder):
        # self.feeder is a function that returns the next line of the Mathics input
        self.feeder = feeder

        # self.input_line is the result of reading the next Mathics input line
        self.input_line: str = feeder.feed()

        # self.pos is current position within self.input_line.
        self.pos = 0

    def feed(self) -> str:
        """
        Return the next line of Mathics input
        """
        return self.feeder.feed()

    # FIXME: Remove this
    def incomplete(self):
        """
        Called by the parser when parsing needs another line of input.
        """
        line: str = self.feed()
        if not line:
            self.feeder.message("Syntax", "sntxi", self.input_line[self.pos :].rstrip())
            raise IncompleteSyntaxError()
        self.input_line += line

    # FIXME: Remove this
    def replace_escape_sequences(self) -> str:
        """
        Replace escape sequences in ``self.input_line``. The replacement string is returned.
        Note: ``self.input_line`` is not modified.
        """

        # Line fragments to be joined before returning from this method.
        line_fragments: List[str] = []

        # Fragment start position of line fragment under consideration.
        self.fragment_start = self.pos

        self.pos = len(self.input_line)

        # In the following loop, we look for and replace escape
        # sequences. The current character under consideration is at
        # self.code[self.pos].  When an escape sequence is found at
        # that position, the previous line_fragment is extracted and
        # stored in ``line_fragments``. The start-position marker for the
        # next line_fragment is started and self.pos is updated.

        # Add the final line fragment.
        line_fragments.append(self.input_line[self.fragment_start :])

        # Produce and return the input line with escape-sequences replaced
        return "".join(line_fragments)

    def sntx_invalid_esc_message(self, char: str):
        """
        Send a "stresc" error message to the input-reading feeder.
        """
        self.feeder.message("Syntax", "stresc", rf"\{char}.")

    def tokenize_escape_sequence(self, source_text: str, pos: int) -> Tuple[str, int]:
        """ """
        result = ""
        c = source_text[pos]
        if c == "\\":
            return "\\", pos + 1

        # https://www.wolfram.com/language/12/networking-and-system-operations/use-the-full-range-of-unicode-characters.html
        # describes hex encoding.
        if c == ".":
            # See if we have a 2-digit hexadecimal number.
            # For example, \.42 is "B"
            result += self.try_parse_base(pos + 1, pos + 3, 16)
            pos += 3
        elif c == ":":
            # See if we have a 4-digit hexadecimal number.
            # For example, \:03B8" is Unicode small leter theta: θ.
            result += self.try_parse_base(pos + 1, pos + 5, 16)
            pos += 5
        elif c == "|":
            # See if we have a 6-digit hexadecimal number.
            result += self.try_parse_base(pos + 1, pos + 7, 16)
            pos += 7
        elif c == "[":
            named_character = self.try_parse_named_character(2)
            if named_character is not None:
                result += named_character
                pos += 4  # ???
        elif c in "01234567":
            # See if we have a 3-digit octal number.
            # For example \065 = "5"
            result += self.try_parse_base(pos, pos + 3, 8)
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
            self.sntx_invalid_esc_message(c)
            raise ScanError()
        return result, pos

    def try_parse_base(self, start_shift: int, end_shift: int, base: int) -> str:
        r"""
        See if characters self.pos+start_shift .. self.pos+end shift
        can be converted to an integer in base  ``base``.

        If so, chr(integer value converted from base).

        However, if the conversion fails, then error messages are
        issued and nothing is updated
        """
        start, end = start_shift, end_shift
        result = None
        if end <= len(self.input_line):
            text = self.input_line[start:end]
            try:
                result = int(text, base)
            except ValueError:
                pass  # result remains None
        if result is None:
            last = end - start
            if last == 2:
                self.feeder.message("Syntax", "sntoct2")
            elif last == 3:
                self.feeder.message("Syntax", "sntoct1")
            elif last == 4:
                self.feeder.message("Syntax", "snthex")
            else:
                raise ValueError()
            self.feeder.message(
                "Syntax", "sntxb", self.input_line[self.pos :].rstrip("\n")
            )
            raise ScanError()

        return chr(result)

    def try_parse_named_character(self, start_shift: int) -> Optional[str]:
        r"""Before calling we have matched "\[".  Scan to the remaining "]" and
        try to match what is found in-between with a known named
        character, e.g. "Theta".  If we can match this, we store
        the unicode character equivalent in ``line_fragments``.
        If we can't find a named character, error messages are
        issued and we leave ``line_fragments`` untouched.
        """
        named_character = self.input_line[
            self.pos + start_shift : self.pos + start_shift
        ]
        if named_character.isalpha():
            char = named_characters.get(named_character)
            if char is None:
                self.feeder.message("Syntax", "sntufn", named_character)
            else:
                return named_character
