# -*- coding: utf-8 -*-


class TranslateError(Exception):
    """A generic class of tokenization errors. This exception is subclassed by other tokenization errors"""

    pass


class ScanError(TranslateError):
    """A generic scanning error"""

    pass


class InvalidSyntaxError(TranslateError):
    """Invalid syntax"""

    pass


class IncompleteSyntaxError(TranslateError):
    """More characters were expected to form a valid token"""

    pass
