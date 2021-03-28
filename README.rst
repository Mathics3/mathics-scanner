|Workflows| |Pypi Installs| |Latest Version| |Supported Python Versions|

|Packaging status|

Mathics Scanner
===============

This is the tokeniser or scanner portion for the Wolfram Language.

As such, it also contains a full set of translation between Wolfram Language
named characters, their Unicode/ASCII equivalents and code-points.

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

To regenerate scanner tables run:

::

   $ mathics-generate-json-table

Implementation
--------------

For notes on the implementation of the packages or details on the conversion
scheme please read ``implementation.rst``.

Contributing
------------

Please feel encouraged to contribute to this package or Mathics! Create your
own fork, make the desired changes, commit, and make a pull request.

License
-------

Mathics is released under the GNU General Public License Version 3 (GPL3).

.. |Workflows| image:: https://github.com/Mathics3/mathics-scanner/workflows/Mathics%20(ubuntu)/badge.svg
.. |Packaging status| image:: https://repology.org/badge/vertical-allrepos/mathics-scanner.svg
			    :target: https://repology.org/project/mathics-scanner/versions
.. |Latest Version| image:: https://badge.fury.io/py/Mathics-Scanner.svg
		 :target: https://badge.fury.io/py/Mathics-Scanner
.. |Pypi Installs| image:: https://pepy.tech/badge/Mathics-Scanner
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/Mathics-Scanner.svg
