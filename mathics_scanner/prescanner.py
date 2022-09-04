# -*- coding: utf-8 -*-
"""
Module for "prescanning". Right now this just means replacing
character escape sequences.
"""

from typing import Callable

from mathics_scanner.characters import named_characters
from mathics_scanner.errors import ScanError, IncompleteSyntaxError


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

    def __init__(self, feeder: Callable):
        # feeder is a function that returns the next line of the Mathics input
        self.feeder = feeder
        self.code = feeder.feed()  # input code
        self.pos = 0  # current position within code

    def feed(self) -> str:
        """
        Return the next line of Mathics input
        """
        return self.feeder.feed()

    def incomplete(self):
        line = self.feed()
        if not line:
            self.feeder.message("Syntax", "sntxi", self.code[self.pos :].rstrip())
            raise IncompleteSyntaxError()
        self.code += line

    def replace_escape_sequences(self) -> str:
        """
        Replace escape sequences in self.code. The replacement string is returned.
        Note: self.code is not modified.
        """

        # Line fragments to be joined before returning from this method.
        line_fragments = []

        # Fragment start position of line fragment under consideration.
        self.fragment_start = self.pos

        def start_new_fragment(pos: int) -> None:
            """
            Update position markers to start a new line fragment at ``pos``.
            """
            self.pos = pos
            self.fragment_start = pos

        def try_parse_base(start_shift: int, end_shift: int, base: int) -> None:
            """
            See if characters self.pos+start_shift .. self.pos+end shift
            can be converted to an integer in base  ``base``.

            If so, we append the characters before the escape sequence without the
            escaping characters like ``\.`` or ``\:``.

            We also append the converted integer to ``line_fragments``, and update
            position cursors for a new line fragment.

            However, if the conversion fails, then error messages are
            issued and nothing is updated
            """
            start, end = self.pos + start_shift, self.pos + end_shift
            result = None
            if end <= len(self.code):
                text = self.code[start:end]
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
                    "Syntax", "sntxb", self.code[self.pos :].rstrip("\n")
                )
                raise ScanError()

            # Add text from prior line fragment as well
            # as the escape sequence, a character, from the escape sequence
            # that was just matched.
            line_fragments.append(self.code[start : self.pos])
            line_fragments.append(chr(result))

            # Set up a new line fragment for the next time we are called.
            start_new_fragment(end)

        def try_parse_named_character(start_shift: int):
            """Before calling we have matched "\[".  Scan to the remaining "]" and
            try to match what is found in-between with a known named
            character, e.g. "Theta".  If we can match this, we store
            the unicode character equivalent in ``line_fragments``.
            If we can't find a named character, error messages are
            issued and we leave ``line_fragments`` untouched.
            """
            i = self.pos + start_shift
            while True:
                if i == len(self.code):
                    self.incomplete()
                if self.code[i] == "]":
                    break
                i += 1

            named_character = self.code[self.pos + start_shift : i]
            if named_character.isalpha():
                char = named_characters.get(named_character)
                if char is None:
                    self.feeder.message("Syntax", "sntufn", named_character)
                    # stay in same line fragment
                else:
                    # Add text from prior line fragment as well
                    # as the escape sequence, a character, from the escape sequence
                    # just matched.
                    line_fragments.append(self.code[self.fragment_start : self.pos])
                    line_fragments.append(char)
                    start_new_fragment(i + 1)

            # Stay in same line fragment, but advance the cursor position.
            self.pos = i + 1

        # In the following loop, we look for and replace escape
        # sequences. The current character under consideration is at
        # self.code[self.pos].  When an escape sequence is found at
        # that position, the previous line_fragment is extracted and
        # stored in ``line_fragments``. The start-position marker for the
        # next line_fragment is started and self.pos is updated.

        while self.pos < len(self.code):
            if self.code[self.pos] == "\\":
                # Look for and handle an escape sequence.
                if self.pos + 1 == len(self.code):
                    self.incomplete()
                c = self.code[self.pos + 1]
                if c == "|":
                    try_parse_base(2, 8, 16)
                if c == ".":
                    # See if we have a two-digit hexadecimal number.
                    try_parse_base(2, 4, 16)
                elif c == ":":
                    # See if we have a four-digit hexadecimal number.
                    try_parse_base(2, 6, 16)
                elif c == "[":
                    try_parse_named_character(2)
                elif c in "01234567":
                    # See if we have an octal number.
                    try_parse_base(1, 4, 8)
                elif c == "\n":
                    if self.pos + 2 == len(self.code):
                        self.incomplete()
                    self.line_fragments.append(
                        self.code[self.fragment_start : self.pos]
                    )
                    start_new_fragment(self.pos + 2)
                else:
                    # Two backslashes in succession indicates a single backslash character.
                    # Advance the scanning cursor (self.pos) over both backslashes.
                    # Also, Python's backslash escape mechanism turns the two backslashes
                    # into one in length calculations.
                    self.pos += 2
            else:
                self.pos += 1

        # Add the final line fragment.
        line_fragments.append(self.code[self.fragment_start :])

        # produce and return the replacement string.
        return "".join(line_fragments)
