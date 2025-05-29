# -*- coding: utf-8 -*-


class ScannerError(Exception):
    """Some sort of error in the scanning or tokenization phase parsing Mathics3.

    There are more specific kinds of exceptions subclassed from this
    exception class.
    """

    def __init__(self, tag: str, *args):
        super().__init__()
        self.name = "Syntax"
        self.tag = tag
        self.args = args


class EscapeSyntaxError(ScannerError):
    """Escape sequence syntax error"""

    pass


class IncompleteSyntaxError(ScannerError):
    """More characters were expected to form a valid token"""

    pass


class InvalidSyntaxError(ScannerError):
    """Invalid syntax"""

    pass


class NamedCharacterSyntaxError(EscapeSyntaxError):
    """Named character syntax error"""

    pass
