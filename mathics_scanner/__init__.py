# -*- coding: utf-8 -*-
"""
This is the tokeniser or scanner portion for the Wolfram Language.

As such, it also contains a full set of translation between Wolfram Language
named characters, their Unicode/ASCII equivalents and code-points.
"""

from mathics_scanner.version import __version__

from mathics_scanner.characters import (
    aliased_characters,
    named_characters,
    replace_unicode_with_wl,
    replace_wl_with_plain_text,
)

# TODO: Move is_symbol_name to the characters module
from mathics_scanner.tokeniser import is_symbol_name, Tokeniser, Token
from mathics_scanner.errors import (
    InvalidSyntaxError,
    IncompleteSyntaxError,
    ScanError,
    TranslateError,
)
from mathics_scanner.feed import (
    LineFeeder,
    SingleLineFeeder,
    FileLineFeeder,
    MultiLineFeeder,
)

__all__ = [
    FileLineFeeder,
    IncompleteSyntaxError,
    InvalidSyntaxError,
    LineFeeder,
    MultiLineFeeder,
    ScanError,
    SingleLineFeeder,
    Token,
    Tokeniser,
    TranslateError,
    __version__,
    aliased_characters,
    is_symbol_name,
    named_characters,
    replace_unicode_with_wl,
    replace_wl_with_plain_text,
]
