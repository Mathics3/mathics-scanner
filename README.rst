|Workflows|

Mathics Scanner
===============

This is the tokeniser or scanner portion for the Wolfram Language.

As such, it also contains a full set of translation between WL Character names, their Unicode names and code points,
and other character metadata such as whether the character is "letter like".

Uses
====

This is used as the scanner inside `Mathics <https://mathics.org>`_ but it can also be used for tokenizing and formatting WL code. In fact we intend to write one.

Implementation
==============

mathics_scaner.characters
-------------------------

This module consists mostly of translation tables between WL and unicode/ascii. 
Because of the large size of this tables, it was decided to store them in a
file and read them from disk at runtime (when the module is imported). Our
tests showed that storing the tables as JSON and using
`ujson <https://github.com/ultrajson/ultrajson>`_ to read them is the most
efficient way to access them. However, this is merelly an implementation
detail and consumers of this library should not relly on this assumption.

For maintainability and effeciency, we decided to store this data in a
human-readable YAML file (`data/named-characters.yml`) and compile them into
the JSON tables used internally by the library (`data/characters.json`) for
faster access at runtime. The conversion of the data is performed by the
script `admin-tools/compile-translation-tables.py` at each commit to the
`master` branch via GitHub Actions.


Contributing
------------

Please feel encouraged to contribute to Mathics! Create your own fork, make the desired changes, commit, and make a pull request.


License
-------

Mathics is released under the GNU General Public License Version 3 (GPL3).

.. |Workflows| image:: https://github.com/Mathics3/mathics-scanner/workflows/Mathics%20(ubuntu)/badge.svg
