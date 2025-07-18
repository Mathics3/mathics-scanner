CHANGES
=======

Jan 26, 2025

1.4.1
-----

Re-release to include ``operators.yml`` into tarball/wheel.


1.4.0
-----

A new operator table, ``operators.yml`` was added to contain
operator information. This information is based information from Robert Jacobson.

See https://github.com/WLTools/LanguageSpec/blob/master/docs/Specification/Syntax/Operator%20Table.csv

From ``operators.yml``, ``operators.json`` is created and
this holds operator information that the Mathics3 Kernel uses.

Things like operator precedence, operator arity, associativity, and
AMSLaTeX equivalent notation is some of the information we store.

All of the 100 or so Unicode operators without initial builtin
meanings, .e.g., \[Cup], \[Cap], ... have been added.

The tokenizer and parser in the Mathics3 Kernel use more YAML table information via JSON extraction. However, more will be done in the future.

A new utility program ``mathics3-tokens`` can be used to show
tokenization of an input stream, with the ``-C`` or ``--CodeTokenize``
option, the program shows the tokens more closely in the form the WMA
CodeTokens package uses. Over time, we expect that our tokenizer will
be more compiliant with CodeTokens.

``named-characters.yml`` was gone over, mostly to fill out
information, such as URL links to Unicode pages.

Operator precedence values have been gone over.


1.3.1
------

Aug 9, 2024

Python 3.8 is now the minimum Python supported. Python 3.12 supported.
Various dependencies elsewhere force 3.8 or newer.


* Packaging was redone to be able to support Python 3.12.
* Files now follow current Python black formatting and isort import ordering
* Some Python code linting

1.3.0
------

* Add escape-code sequence for 32-bit Unicode. Issue #48.
* Correct ``Infix`` and ``Tilde`` character symbols
* Support double backslash (``\\``) as a single backslash character (``\``).
* Correct Unicode for ScriptN and ScriptCaptialN
* Correct a number of is-letter-like entries.
* Accept \u21A6 as symbol for Function.
* Change the precedence of ``|->``(``Function`` symbol) to 800 so it isn't interpreted as a ``|``
  followed by ``->``
* ASCII operator tables can now be generated
* Add DifferentialD and Integrate even though we don't have a full set of prefix operators.
* more precedence values added to operators
* Python 3.11 operation verified


1.2.4
-----

* Start adding AMSLateX names.
* Add ``ApplyTo``, and ``Factorial2``.
* Adjust ``Tilde``, and ``Factorial``.
* Regularize unicode equivalents.
* Add named-characters.yml to distribution packages; Issue #32.
* Use SPDX identifier in license; PR #31.

1.2.2-1.2.3
-----

Redo for packaging problems.

Many thanks to Victor the packager for AUR for pointing this out.

1.2.1
-----

* Add tables for operator precedence.
* Start to add AMSLaTeX symbols. (A future release will finish this)
* Revise ``README.rst``.
* Some small corrections: ``Implies``
* Make ``ujson`` optional


1.2.0
-----

Tag unicode operators which have no definition and add the ability to dump them. This is useful for mathics-pygments.


1.1.2
-----

Release 1.1.1 introduced a small bad interaction with Mathics and the
unicode infix form of ``Function[]``.

In our master table, when there is a unicode operator like there is for "Function",
(uF4A1), the operator name to be YAML key name.

There is an alternate ASCII Function operator ``&``. And for that we
used the name Function which precluded using it for the unicode, where
it is mandiatory. For ASCII operators it isn't necessary, but still
nice to do when there is no conflict.

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
