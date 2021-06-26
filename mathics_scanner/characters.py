# -*- coding: utf-8 -*-
"""
The ``mathics_scanner.characters`` module consists mostly of translation tables
between Wolfram's internal representation of `named characters
<https://reference.wolfram.com/language/tutorial/InputAndOutputInNotebooks.html#4718>`_
and Unicode/ASCII.
"""

import re
import os
import pkg_resources

try:
    import ujson
except ImportError:
    import json as ujson

ROOT_DIR = pkg_resources.resource_filename("mathics_scanner", "")

# Load the conversion tables from disk
characters_path = os.path.join(ROOT_DIR, "data", "characters.json")
if os.path.exists(characters_path):
    with open(characters_path, "r") as f:
        _data = ujson.load(f)
else:
    _data = {}

# Character ranges of letters
_letters = "a-zA-Z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u0103\u0106\u0107\
\u010c-\u010f\u0112-\u0115\u011a-\u012d\u0131\u0141\u0142\u0147\u0148\
\u0150-\u0153\u0158-\u0161\u0164\u0165\u016e-\u0171\u017d\u017e\
\u0391-\u03a1\u03a3-\u03a9\u03b1-\u03c9\u03d1\u03d2\u03d5\u03d6\
\u03da-\u03e1\u03f0\u03f1\u03f5\u210a-\u210c\u2110-\u2113\u211b\u211c\
\u2128\u212c\u212d\u212f-\u2131\u2133-\u2138\uf6b2-\uf6b5\uf6b7\uf6b9\
\uf6ba-\uf6bc\uf6be\uf6bf\uf6c1-\uf700\uf730\uf731\uf770\uf772\uf773\
\uf776\uf779\uf77a\uf77d-\uf780\uf782-\uf78b\uf78d-\uf78f\uf790\
\uf793-\uf79a\uf79c-\uf7a2\uf7a4-\uf7bd\uf800-\uf833\ufb01\ufb02"

# Character ranges of letterlikes
_letterlikes = _data.get("letterlikes", {})

# Conversion from WL to the fully qualified names
_wl_to_ascii = _data.get("wl-to-ascii-dict", {})
_wl_to_ascii_re = re.compile(_data.get("wl-to-ascii-re", ""))

# Conversion from WL to unicode
_wl_to_unicode = _data.get("wl-to-unicode-dict", {})
_wl_to_unicode_re = re.compile(_data.get("wl-to-unicode-re", ""))

# Conversion from unicode to WL
_unicode_to_wl = _data.get("unicode-to-wl-dict", {})
_unicode_to_wl_re = re.compile(_data.get("unicode-to-wl-re", ""))

# All supported named characters
named_characters = _data.get("named-characters", {})

# ESC sequence aliases
aliased_characters = _data.get("aliased-characters", {})


def replace_wl_with_plain_text(wl_input: str, use_unicode=True) -> str:
    """
    The Wolfram Language uses specific Unicode characters to represent Wolfram
    Language named characters. This functions replaces all occurrences of such
    characters with their corresponding Unicode/ASCII equivalents.

    :param wl_input: The string whose characters will be replaced.
    :param use_unicode: A flag that indicates whether to use Unicode or ASCII
                        for the conversion.

    Note that the occurrences of named characters in ``wl_input`` are expect to
    be represented by Wolfram's internal scheme. For more information Wolfram's
    representation scheme and on our own conversion scheme please see `Listing
    of Named Characters
    <https://reference.wolfram.com/language/guide/ListingOfNamedCharacters.html>`_
    and ``implementation.rst`` respectively.
    """
    r = _wl_to_unicode_re if use_unicode else _wl_to_ascii_re
    d = _wl_to_unicode if use_unicode else _wl_to_ascii

    return r.sub(lambda m: d[m.group(0)], wl_input)


def replace_unicode_with_wl(unicode_input: str) -> str:
    """
    The Wolfram Language uses specific Unicode characters to represent Wolfram
    Language named characters. This functions replaces all occurrences of the
    corresponding Unicode equivalents of such characters with the characters
    themselves.

    :param unicode_input: The string whose characters will be replaced.

    Note that the occurrences of named characters in the output of
    ``replace_unicode_with_wl`` are represented using Wolfram's internal
    scheme. For more information Wolfram's representation scheme and on our own
    conversion scheme please see `Listing of Named Characters
    <https://reference.wolfram.com/language/guide/ListingOfNamedCharacters.html>`_
    and ``implementation.rst`` respectively.
    """
    return _unicode_to_wl_re.sub(lambda m: _unicode_to_wl[m.group(0)], unicode_input)
