# -*- coding: utf-8 -*-


class SyntaxError(Exception):
    """Some sort of error in the scanning or tokenization phase parsing Mathics3.

    There are more specific kinds of exceptions subclassed from this
    exception class.
    """

    def __init__(self, tag: str, *args):
        super().__init__()
        self.name = "Syntax"
        self.tag = tag
        self.args = args


class EscapeSyntaxError(SyntaxError):
    """Escape sequence syntax error"""

    pass


class IncompleteSyntaxError(SyntaxError):
    """More characters were expected to form a valid token"""

    pass


class InvalidSyntaxError(SyntaxError):
    """Invalid syntax"""

    pass


class NamedCharacterSyntaxError(EscapeSyntaxError):
    """Named character syntax error"""

    pass
