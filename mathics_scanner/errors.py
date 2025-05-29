# -*- coding: utf-8 -*-


class TranslateErrorNew(Exception):
    def __init__(self, tag: str, *args):
        super().__init__()
        self.name = "Syntax"
        self.tag = tag
        self.args = args


class TranslateError(Exception):
    """
    A generic class of tokenization errors. This exception is subclassed by other
    tokenization errors
    """


class EscapeSyntaxError(TranslateErrorNew):
    """Escape sequence syntax error"""

    pass


class IncompleteSyntaxError(TranslateErrorNew):
    """More characters were expected to form a valid token"""

    pass


class InvalidSyntaxError(TranslateErrorNew):
    """Invalid syntax"""

    pass


class NamedCharacterSyntaxError(TranslateErrorNew):
    """Named character syntax error"""

    pass


class ScanError(TranslateErrorNew):
    """A generic scanning error"""

    pass
