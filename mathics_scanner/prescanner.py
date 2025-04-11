# -*- coding: utf-8 -*-
"""
Module for "prescanning". Right now this just means replacing
character escape sequences.
"""

from typing import List

from mathics_scanner.errors import IncompleteSyntaxError
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
