# -*- coding: utf-8 -*-
"""
Wolfram-language scanner
"""

from mathics_scanner.version import __version__

from mathics_scanner.characters import (
    aliased_characters,
    named_characters,
    replace_unicode_with_wl,
    replace_wl_with_plain_text,
)
from mathics_scanner.tokeniser import is_symbol_name, Tokeniser
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
