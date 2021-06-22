# -*- coding: utf-8 -*-
"""
Rather than trying to parse all the lines of code at once, this module implements methods
for returning one line code at a time.
"""

from abc import abstractmethod, ABCMeta


class LineFeeder(metaclass=ABCMeta):
    """An abstract representation for reading lines of characters, a
    "feeder". The purpose of a feeder is to mediate the consumption of
    characters between the tokeniser and the actual file being scaned,
    as well to store messages regarding tokenization errors.
    """

    def __init__(self, filename: str):
        """
        :param filename: A string that describes the source of the feeder, i.e.
                         the filename that is being feed.
        """
        self.messages = []
        self.lineno = 0
        self.filename = filename

    @abstractmethod
    def feed(self):
        """
        Consume and return next line of code. Each line should be followed by a
        newline character. Returns '' after all lines are consumed.
        """

        return ""

    @abstractmethod
    def empty(self) -> bool:
        """
        Return True once all lines have been consumed.
        """

        return True

    def message(self, sym: str, tag: str, *args) -> None:
        """
        Append a generic message of type ``sym`` to the message queue.
        """

        if sym == "Syntax":
            message = self.syntax_message(sym, tag, *args)
        else:
            message = [sym, tag] + list(args)
        self.messages.append(message)

    def syntax_message(self, sym: str, tag: str, *args):
        """
        Append a message concerning syntax errors to the message queue.
        """

        if len(args) > 3:
            raise ValueError("Too many args.")
        message = [sym, tag]
        for i in range(3):
            if i < len(args):
                message.append(f'"{args[i]}"')
            else:
                message.append('""')
        message.append(str(self.lineno))
        message.append(f'"{self.filename}"')
        assert len(message) == 7
        return message

    # # TODO: Rethink this?
    # def syntax_message(self, sym: str, tag, *args):
    #     for message in self.messages:
    #         evaluation.message(*message)
    #     self.messages = []


class MultiLineFeeder(LineFeeder):
    "A feeder that feeds one line at a time."

    def __init__(self, lines, filename=""):
        """
        :param lines: The source of the feeder (a string).
        :param filename: A string that describes the source of the feeder, i.e.
                         the filename that is being feed.
        """
        super(MultiLineFeeder, self).__init__(filename)
        self.lineno = 0
        if isinstance(lines, str):
            self.lines = lines.splitlines(True)
        else:
            self.lines = lines

    def feed(self):
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

    def __init__(self, code, filename=""):
        """
        :param code: The source of the feeder (a string).
        :param filename: A string that describes the source of the feeder, i.e.
                         the filename that is being feed.
        """
        super().__init__(filename)
        self.code = code
        self._empty = False

    def feed(self):
        if self._empty:
            return ""
        self._empty = True
        self.lineno += 1
        return self.code

    def empty(self) -> bool:
        return self._empty


class FileLineFeeder(LineFeeder):
    "A feeder that feeds lines from an open ``File`` object"

    def __init__(self, fileobject, trace_fn=None):
        """
        :param fileobject: The source of the feeder (a string).
        :param filename: A string that describes the source of the feeder,
                           i.e.  the filename that is being feed.
        """
        super().__init__(fileobject.name)
        self.fileobject = fileobject
        self.lineno = 0
        self.eof = False
        self.trace_fn = trace_fn

    def feed(self) -> str:
        result = self.fileobject.readline()
        while result == "\n":
            result = self.fileobject.readline()
            self.lineno += 1
            if self.trace_fn:
                self.trace_fn("%5d: %s" % (self.lineno, result), end="")
        if result:
            self.lineno += 1
        else:
            self.eof = True
        return result

    def empty(self) -> bool:
        return self.eof
