#!/bin python3
"""
Creates GNU Readline inputrc tables for converting WL escape sequences to either
unicode symbols or WL Character strings
"""
import sys

from mathics_scanner.characters import replace_wl_with_plain_text as r
from mathics_scanner.characters import aliased_characters

def _escape(s: str) -> str:
    """Escapes special chracters in inputrc strings"""
    return s.replace("\\", "\\\\").replace("\"", "\\\"")

def _format(c: str, use_unicode: bool) -> str:
    """Formats a single key-value pair"""
    key = _escape(c)
    val = _escape(r(aliased_characters[c], use_unicode=use_unicode))

    return f'"\\e{key}\\e": "{val}"\n'

def generate_inputrc(fd=sys.stdout, use_unicode=True) -> None:
    """
    Generates inputrc files that maps WL ESC sequence aliases to their 
    corresponding plain-text representation (full Unicode or strick ASCII)
    """
    for alias in aliased_characters:
        fd.write(_format(alias, use_unicode))

if __name__ == "__main__":
    if sys.argv[1] == "inputrc-unicode":
        generate_inputrc(use_unicode=True)
    elif sys.argv[1] == "inputrc-no-unicode":
        generate_inputrc(use_unicode=False)

