===
API
===

.. automodule:: mathics_scanner
  :members: is_symbol_name

Tokenization
============

Tokenization is performed by the ``Tokeniser`` class. The ``next`` method
consumes characters from a feeder and returns a token if the tokenization
succeeds. If the tokenization fails an instance of ``ScannerError`` is
raised.

.. autoclass:: Tokeniser(object)
  :members: __init__, incomplete, sntx_message, next

The tokens returned by ``next`` are instances of the ``Token`` class:

.. autoclass:: Token(object)
  :members: __init__
  :special-members:

Feeders
=======

A feeder is an intermediate between the tokeniser and the actual file being scanned. Feeders used by the tokeniser are instances of the ``LineFeeder`` class:

.. autoclass:: LineFeeder(object)
  :members: feed, empty, message, syntax_message

Specialized Feeders
-------------------

To read multiple lines of code at a time use the ``MultiLineFeeder`` class:

.. autoclass:: MultiLineFeeder(LineFeeder)
  :members: __init__

To read a single line of code at a time use the ``SingleLineFeeder`` class:

.. autoclass:: SingleLineFeeder(LineFeeder)
  :members: __init__

To read lines of code from a file use the ``FileLineFeeder`` class:

.. autoclass:: FileLineFeeder(LineFeeder)
  :members: __init__

Character Conversions
=====================

.. automodule:: mathics_scanner.characters
  :members: replace_wl_with_plain_text, replace_unicode_with_wl

The ``mathics_scanner.characters`` module also exposes special dictionaries:

``named_characters``
  Maps fully qualified names of named characters to their corresponding
  code-points in Wolfram's internal representation:

.. code-block:: python

  for named_char, code in named_characters.items():
    print(f"The named character {named_char} maps to U+{ord(code):X}")

``aliased_characters``
  Maps the ESC sequence alias of all aliased characters to their corresponding
  code points in Wolfram's internal representation.

mathics_scanner.generate.rl_inputrc
-----------------------------------

.. automodule:: mathics_scanner.generate.rl_inputrc
  :members: generate_inputrc
