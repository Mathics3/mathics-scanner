#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import ujson
import os
import pkg_resources

ROOT_DIR = pkg_resources.resource_filename("mathics_scanner", "")

# Load the conversion tables from disk
with open(os.path.join(ROOT_DIR, "data/characters.json"), "r") as f:
    _data = ujson.load(f)

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
_letterlikes = _data["letterlikes"]

# Conversion from WL to the fully qualified names
wl_to_ascii = _data["wl-to-ascii-dict"]
_wl_to_ascii_re = re.compile(_data["wl-to-ascii-re"])

# Conversion from WL to unicode
wl_to_unicode = _data["wl-to-unicode-dict"]
_wl_to_unicode_re = re.compile(_data["wl-to-unicode-re"])

# Conversion from unicode to WL
unicode_to_wl = _data["unicode-to-wl-dict"]
_unicode_to_wl_re = re.compile(_data["unicode-to-wl-re"])

# All supported named characters
named_characters = _data["named-characters"]

# ESC sequence aliases
aliased_characters = _data["aliased-characters"]

def replace_wl_with_plain_text(wl_input: str, use_unicode=True) -> str:
    """
    WL uses some non-unicode character for various things.
    Replace them with the unicode equivalent.
    """
    r = _wl_to_unicode_re if use_unicode else _wl_to_ascii_re
    d = wl_to_unicode if use_unicode else wl_to_ascii

    return r.sub(lambda m: d[m.group(0)], wl_input)

def replace_unicode_with_wl(unicode_input: str) -> str:
    """
    WL uses some non-unicode character for various things.
    Replace their unicode equivalent with them.
    """
    return _unicode_to_wl_re.sub(
        lambda m: unicode_to_wl[m.group(0)], unicode_input
    )

