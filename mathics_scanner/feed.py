# -*- coding: utf-8 -*-
"""
Rather than trying to parse all the lines of code at once, this module implements
methods for returning one line code at a time.
"""

from abc import ABCMeta, abstractmethod
from typing import Callable, List, Optional

import mathics_scanner
from mathics_scanner.location import MATHICS3_PATHS, ContainerKind


class LineFeeder(metaclass=ABCMeta):
    """An abstract representation for reading lines of characters, a
    "feeder". The purpose of a feeder is to mediate the consumption of
    characters between the tokeniser and the actual file being scanned,
    as well to store messages regarding tokenization errors.
    """

    def __init__(self, container, container_kind=ContainerKind.UNKNOWN):
        """
        :param container_name: A string that describes the source of
          the feeder, i.e. the file path that is being feed, or the
          Python source code path, or an open terminal shell stream.
        """

        # A message is a list that starts out with a "symbol_name", like "Part",
        # a message tag, like "partw", and a list of argument to be used in
        # creating a message in list of messages.
        self.messages: List[list] = []

        self.lineno: int = 0
        self.container = container
        self.container_kind = container_kind
        self.source_text: Optional[str] = None

        self.container_index = -1

        # Note: fully qualified name is needed to pick up dynamic changes
        if mathics_scanner.location.TRACK_LOCATIONS and container:
            if container_kind == ContainerKind.FILE:
                if container in MATHICS3_PATHS:
                    self.container_index = MATHICS3_PATHS.index(container)
                else:
                    self.container_index = len(MATHICS3_PATHS)
                    MATHICS3_PATHS.append(container)
            elif container_kind == ContainerKind.STREAM:
                self.container.append(self.source_text)

    @abstractmethod
    def feed(self) -> str:
        """
        Consume and return next line of code. Each line should be followed by a
        newline character. Returns '' after all lines are consumed.
        """
        ...

    @abstractmethod
    def empty(self) -> bool:
        """
        Return True once all lines have been consumed.
        """
        ...

    def message(self, symbol_name: str, tag: str, *args) -> None:
        """

        A Generic routine for appending a message to the ``self.messages`` message
        queue.

        ``symbol_name`` is usually the string symbol name of the built-in function that
        is recording the error. "Syntax" error is the exception to this rule.

        ``tag`` specifies a class of errors that this error belongs to.

        ``*args`` are the specific message arguments. Usually (but not here)
        the arguments are used to fill out a template specified by ``tag``

        For example, consider this message displayed:

            Part::partw: Part {10} of abcde does not exist.

        "Part" is the symbol_name, "partw" is the tag and args is:
        (<ListExpression: (<Integer: 10>,)>, <String: "abcde">)

        """

        if symbol_name == "Syntax":
            next_message = self.syntax_message(symbol_name, tag, *args)
        else:
            next_message = [symbol_name, tag] + list(args)

        self.messages.append(next_message)

    def syntax_message(self, symbol_name: str, tag: str, *args) -> List[str]:
        """
        Append a "Syntax" error message to the message queue.
        """

        if len(args) > 3:
            raise ValueError("Too many args.")
        message = [symbol_name, tag]
        for i in range(3):
            if i < len(args):
                message.append(f'"{args[i]}"')
            else:
                message.append('""')
        message.append(str(self.lineno))
        if self.container:
            message.append(f'"{self.container}"')
        elif len(args) == 2:
            message.append(f'"{(args[1].rstrip())}"')
        else:
            message.append("")
        assert len(message) == 7
        return message

    # # TODO: Rethink this?
    # def syntax_message(self, sym: str, tag, *args):
    #     for message in self.messages:
    #         evaluation.message(*message)
    #     self.messages = []


class MultiLineFeeder(LineFeeder):
    "A feeder that feeds one line at a time."

    def __init__(self, lines, container, container_kind=ContainerKind.UNKNOWN):
        """
        :param lines: The source of the feeder (a string).
        :param container_name: A string that describes the source of the feeder,
          i.e. the file path that is being feed.
        """
        super(MultiLineFeeder, self).__init__(container, container_kind)
        self.lineno = 0

        if isinstance(lines, str):
            self.lines = lines.splitlines(True)
        else:
            self.lines = lines

    def feed(self) -> str:
        if self.lineno < len(self.lines):
            result = self.lines[self.lineno]
            self.lineno += 1
        else:
            result = ""
        return result

    def empty(self) -> bool:
        return self.lineno >= len(self.lines)


class SingleLineFeeder(LineFeeder):
    "A feeder that feeds all the code as a single line."

    def __init__(
        self, source_text: str, container, container_kind=ContainerKind.UNKNOWN
    ):
        """
        :param source_text: The source of the feeder (a string).
        :param filename: A string that describes the source of the feeder, i.e.
                         the filename that is being feed.
        """
        super().__init__(container, container_kind)
        self.source_text = source_text
        if container_kind == ContainerKind.STREAM:
            self.container.append[source_text]
        self._empty = False

    def feed(self) -> str:
        if self._empty:
            return ""
        self._empty = True
        self.lineno += 1
        return self.source_text

    def empty(self) -> bool:
        return self._empty


class FileLineFeeder(LineFeeder):
    "A feeder that feeds lines from an open ``File`` object"

    def __init__(self, fileobject, trace_fn: Optional[Callable] = None):
        """
        :param fileobject: The source of the feeder (a string).
        :param filename: A string that describes the source of the feeder,
                           i.e.  the filename that is being feed.
        """
        super().__init__(fileobject.name, container_kind=ContainerKind.FILE)
        self.fileobject = fileobject
        self.lineno = 0
        self.eof = False
        self.trace_fn = trace_fn
        self.source_text = ""

    def feed(self) -> str:
        result = self.fileobject.readline()
        self.source_text += result
        while result == "\n":
            result = self.fileobject.readline()
            self.lineno += 1
            self.source_text += result

            if self.trace_fn:
                self.trace_fn(self.lineno, result)
        if result:
            self.lineno += 1
        else:
            self.eof = True
        return result

    def empty(self) -> bool:
        return self.eof
