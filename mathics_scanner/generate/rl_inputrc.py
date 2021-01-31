#!/bin python3
"""
Creates GNU Readline inputrc tables for converting WL escape sequences to either
unicode symbols or WL Character strings
"""
import sys

from mathics_scanner.characters import replace_wl_with_plain_text as r
from mathics_scanner.characters import aliased_characters

def escape(s: str) -> str:
    """Escapes special chracters in inputrc strings"""
    return s.replace("\\", "\\\\").replace("\"", "\\\"")

def format(c: str, use_unicode: bool) -> str:
    """Formats a single key-value pair"""
    key = escape(c)
    val = escape(r(aliased_characters[c], use_unicode=use_unicode))

    return f'"\\e{key}\\e": "{val}"\n'

def generate_inputrc_unicode(fd=sys.stdout) -> None:
        fd.write("# GNU Readline input translations\n\n")
        fd.write("# Lowercase TeX Greek characters\n")
        fd.write("$include inputrc-greek-letters\n\n")
        fd.write("# Autogenerated with mathics-scanner\n")

        for alias in aliased_characters:
            fd.write(format(alias, use_unicode=True))

def generate_inputrc_no_unicode(fd=sys.stdout) -> None:
    # Generate inputrc-no-unicode
    fd.write("# GNU Readline input translations\n\n")
    fd.write("# Autogenerated with mathics-scanner\n")

    for alias in aliased_characters:
        fd.write(format(alias, use_unicode=False))

if __name__ == "__main__":
    if sys.argv[1] == "inputrc-unicode":
        generate_inputrc_unicode()
    elif sys.argv[1] == "inputrc-no-unicode":
        generate_inputrc_no_unicode()
