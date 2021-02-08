=====================
Using mathics-scanner
=====================

Uses
----

This is used as the scanner inside `Mathics <https://mathics.org>`_ but it can
also be used for tokenizing and formatting Wolfram Language code. In fact we
intend to write one. This library is also quite usefull if you need to work
with Wolfram Language named character and convert them to various formats.

Usage
-----

- For tokenizing and scanning Wolfram Language code, use the
  ``mathics_scanner.tokenizer.Tokenizer`` class.
- To convert between Wolfram Language named characters and Unicode/ASCII, use
  the ``mathics_scanner.characters.replace_wl_with_plain_text`` and
  ``mathics_scanner.characters.replace_unicode_with_wl`` functions.
- To convert between qualified names of named characters (such ``FormalA`` for
  ``\[FormalA]``) and Wolfram's internal representation use the
  ``m̀athics_scanner.characters.named_characters`` dictionary.

