|Workflows| |Pypi Installs| |Latest Version| |Supported Python Versions|

|Packaging status|

Mathics Character Tables and Scanner
=====================================

This repository really contains two things:

* extensive tables describing WL symbols and operators their properties
* a tokenizer or scanner portion for the Wolfram Language.

With respect to the first item, there is a commented YAML that contains a
full set of translation between:

* Wolfram Language named characters,
* their Unicode/ASCII equivalents and Unicode and WL code-points,
* Operator name (if symbol is an operator),
* Operator precedence (if an operator)
* Keyboard escape sequences for the symbol

Uses
----

The scanner and character tables are used inside `Mathics <https://mathics.org>`_. However information can
also be used by other programs for tokenizing and formatting Wolfram Language code.

For example, tables are used in `mathics-pygments <https://pypi.org/project/Mathics-Scanner/>`_, a Pygments-based
lexer and highlighter for Mathematica/Wolfram Language source code.

This library may be useful if you need to work with Wolfram Language
named character and convert them to various formats.

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

To regenerate JSON-format tables run:

::

   $ mathics-generate-json-table

Without options ``mathics-generate-json-table`` produces the maximum set of correspondences.

In most applications though you may need just a few of these. The
``--field`` option can be used to narrow the list of entries to output in JSON. Run
``mathics-generate-json-table --help`` for a full list of fields.


Implementation
--------------

For notes on the implementation of the packages or details on the conversion
scheme please read `Implementation <https://mathics-scanner.readthedocs.io/en/latest/implementation.html>`_.

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
