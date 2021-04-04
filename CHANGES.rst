CHANGES
=======

1.1.1
-----

* Finish adding operator names.
* Generate ``IndentingNewline`` (``\n``) properly in GNU Readline inputrc tables.
* Adjust expectation on test since there can be duplicate function operators (for ``Apply`` and ``Function``).

1.1.0
-----

* Add operator-name, and ASCII fields. See named-characters.yml for a description of these
* Add some whitespace characters like IndentingNewLine and RawReadLine
* Improve testing
* Fix some small tagging based on testing
* Add unicode-to-operator generation

Note: not all operators have been tagged, so expect another release soon when that's done.


1.0.0
-----

* The scanner split off from Mathics3.
* Tables added for converting between WL names and Unicode, ASCII and character properties. See ``implementation.rst`` for details.
* Code and docstring gone over.

See git in Mathics before Jan 18, 2021 for old history of these files.
