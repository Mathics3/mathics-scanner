# -*- coding: utf-8 -*-


import re
import string
from typing import Optional

from mathics_scanner.characters import _letterlikes, _letters
from mathics_scanner.errors import ScanError
from mathics_scanner.prescanner import Prescanner

# special patterns
NUMBER_PATTERN = r"""
( (?# Two possible forms depending on whether base is specified)
    (\d+\^\^([a-zA-Z0-9]+\.?[a-zA-Z0-9]*|[a-zA-Z0-9]*\.?[a-zA-Z0-9]+))
    | (\d+\.?\d*|\d*\.?\d+)
)
(``?(\+|-)?(\d+\.?\d*|\d*\.?\d+)|`)?        (?# Precision / Accuracy)
(\*\^(\+|-)?\d+)?                           (?# Exponent)
"""
base_symbol_pattern = r"((?![0-9])([0-9${0}{1}])+)".format(_letters, _letterlikes)
full_symbol_pattern_str = r"(`?{0}(`{0})*)".format(base_symbol_pattern)
pattern_pattern = r"{0}?_(\.|(__?)?{0}?)?".format(full_symbol_pattern_str)
slot_pattern = r"\#(\d+|{0})?".format(base_symbol_pattern)
FILENAME_PATTERN = r"""
(?P<quote>\"?)                              (?# Opening quotation mark)
    [a-zA-Z0-9\`/\.\\\!\-\:\_\$\*\~\?]+     (?# Literal characters)
(?P=quote)                                  (?# Closing quotation mark)
"""
NAMES_WILDCARDS = "@*"
base_names_pattern = r"((?![0-9])([0-9${0}{1}{2}])+)".format(
    _letters, _letterlikes, NAMES_WILDCARDS
)
full_names_pattern = r"(`?{0}(`{0})*)".format(base_names_pattern)

tokens = [
    ("Definition", r"\? "),
    ("Information", r"\?\? "),
    ("Number", NUMBER_PATTERN),
    ("String", r'"'),
    ("Pattern", pattern_pattern),
    ("Symbol", full_symbol_pattern_str),
    ("SlotSequence", r"\#\#\d*"),
    ("Slot", slot_pattern),
    ("Out", r"\%(\%+|\d+)?"),
    ("PutAppend", r"\>\>\>"),
    ("Put", r"\>\>"),
    ("Get", r"\<\<"),
    ("RawLeftBracket", r" \[ "),
    ("RawRightBracket", r" \] "),
    ("RawLeftBrace", r" \{ "),
    ("RawRightBrace", r" \} "),
    ("RawLeftParenthesis", r" \( "),
    ("RawRightParenthesis", r" \) "),
    ("RawLeftAssociation", r" \<\| "),
    ("RawRightAssociation", r" \|\> "),
    ("RawComma", r" \, "),
    ("Span", r" \;\; "),
    ("MessageName", r" \:\: "),
    #
    # Enclosing Box delimiters
    #
    ("LeftRowBox", r" \\\( "),
    ("RightRowBox", r" \\\) "),
    # Box Operators which are valid only inside Box delimiters
    ("InterpretedBox", r" \\\! "),
    ("SuperscriptBox", r" \\\^ "),
    ("SubscriptBox", r" \\\_ "),
    ("OverscriptBox", r" \\\& "),
    ("UnderscriptBox", r" \\\+ "),
    ("OtherscriptBox", r" \\\% "),
    ("FractionBox", r" \\\/ "),
    ("SqrtBox", r" \\\@ "),
    ("RadicalBox", r" \\\@ "),
    ("FormBox", r" \\\` "),
    #
    # End Box Operators
    #
    ("Information", r"\?\?"),
    ("PatternTest", r" \? "),
    ("Increment", r" \+\+ "),
    ("Decrement", r" \-\- "),
    ("MapAll", r" \/\/\@ "),
    ("Map", r" \/\@ "),
    ("ApplyList", r" \@\@\@ "),
    ("Apply", r" \@\@ "),
    ("Composition", r" \@\* "),
    ("Prefix", r" \@ "),
    ("StringExpression", r" \~\~ "),
    ("Infix", r" \~ "),
    ("Derivative", r" \' "),
    ("StringJoin", r" \<\> "),
    ("NonCommutativeMultiply", r" \*\* "),
    ("AddTo", r" \+\= "),
    ("SubtractFrom", r" \-\=  "),
    ("TimesBy", r" \*\= "),
    ("DivideBy", r" \/\=  "),
    ("Times", r" \*|\u00d7 "),
    ("SameQ", r" \=\=\= "),
    ("UnsameQ", r" \=\!\= "),
    ("Equal", r" (\=\=) | \uf431 | \uf7d9 "),
    ("Unequal", r" (\!\= ) | \u2260 "),
    ("LessEqual", r" (\<\=) | \u2264 "),
    ("LessSlantEqual", r" \u2a7d "),
    ("GreaterEqual", r" (\>\=) | \u2265 "),
    ("GreaterSlantEqual", r" \u2a7e "),
    ("Greater", r" \> "),
    ("Less", r" \< "),
    # https://reference.wolfram.com/language/ref/character/DirectedEdge.html
    # The official Unicode value is \u2192.
    ("DirectedEdge", r" -> | \uf3d5|\u2192"),
    ("Or", r" (\|\|) | \u2228 "),
    ("And", r" (\&\&) | \u2227 "),
    ("RepeatedNull", r" \.\.\. "),
    ("Repeated", r" \.\. "),
    ("Alternatives", r" \| "),
    ("Rule", r" (\-\>)|\uF522 "),
    ("RuleDelayed", r" (\:\>)|\uF51F "),
    # https://reference.wolfram.com/language/ref/character/UndirectedEdge.html
    # The official Unicode value is \u2194
    ("UndirectedEdge", r" (\<\-\>)|\u29DF|\u2194 "),
    ("ReplaceRepeated", r" \/\/\. "),
    ("ReplaceAll", r" \/\. "),
    ("RightComposition", r" \/\* "),
    ("Postfix", r" \/\/ "),
    ("UpSetDelayed", r" \^\:\= "),
    ("SetDelayed", r" \:\= "),
    ("UpSet", r" \^\= "),
    ("TagSet", r" \/\: "),
    ("Unset", r" \=\s*\.(?!\d|\.) "),  # allow whitespace but avoid e.g. x=.01
    ("Set", r" \= "),
    ("Condition", r" \/\; "),
    ("Semicolon", r" \; "),
    ("Divide", r" \/|\u00f7 "),
    ("Power", r" \^ "),
    ("Dot", r" \. "),
    ("Minus", r" \-|\u2212 "),
    ("Plus", r" \+ "),
    ("RawBackslash", r" \\ "),
    ("Factorial2", r" \!\! "),
    ("Factorial", r" \! "),
    ("Function", r" \& | \uF4A1 | \u21A6 | \|-> "),
    ("RawColon", r" \: "),
    # ('DiscreteShift', r' \uf4a3 '),
    # ('DiscreteRatio', r' \uf4a4 '),
    # ('DifferenceDelta', r' \u2206 '),
    # ('PartialD', r' \u2202 '),
    # uf4a0 is Wolfram custom, u2a2f is standard unicode
    ("Cross", r" \uf4a0 | \u2a2f"),
    ("Colon", r" \u2236 "),
    # uf3c7 is Wolfram custom, 1d40 is standard unicode
    ("Transpose", r" \uf3c7 | \u1d40"),
    ("Conjugate", r" \uf3c8 "),
    ("ConjugateTranspose", r" \uf3c9 "),
    ("HermitianConjugate", r" \uf3ce "),
    ("Integral", r" \u222b "),
    ("DifferentialD", r" \U0001D451 | \uf74c"),
    ("Del", r" \u2207 "),
    # uf520 is Wolfram custom, 25ab is standard unicode
    ("Square", r" \uf520 | \u25ab"),
    ("SmallCircle", r" \u2218 "),
    ("CircleDot", r" \u2299 "),
    # ('Sum', r' \u2211 '),
    # ('Product', r' \u220f '),
    ("PlusMinus", r" \u00b1 "),
    ("MinusPlus", r" \u2213 "),
    ("Nor", r" \u22BD "),
    ("Nand", r" \u22BC "),
    ("Xor", r" \u22BB "),
    ("Xnor", r" \uF4A2 "),
    ("Diamond", r" \u22c4 "),
    ("Wedge", r" \u22c0 "),
    ("Vee", r" \u22c1 "),
    ("CircleTimes", r" \u2297 "),
    ("CenterDot", r" \u00b7 "),
    ("Star", r" \u22c6"),
    ("VerticalTilde", r" \u2240 "),
    ("Coproduct", r" \u2210 "),
    ("Cap", r" \u2322 "),
    ("Cup", r" \u2323 "),
    ("CirclePlus", r" \u2295 "),
    ("CircleMinus", r" \u2296 "),
    ("Intersection", r" \u22c2 "),
    ("Union", r" \u22c3 "),
    ("VerticalBar", r" \u2223 "),
    ("NotVerticalBar", r" \u2224 "),
    ("DoubleVerticalBar", r" \u2225 "),
    ("NotDoubleVerticalBar", r" \u2226 "),
    ("Element", r" \u2208 "),
    ("NotElement", r" \u2209 "),
    ("Subset", r" \u2282 "),
    ("Superset", r" \u2283 "),
    ("ForAll", r" \u2200 "),
    ("Exists", r" \u2203 "),
    ("NotExists", r" \u2204 "),
    ("Not", r" \u00AC "),
    ("Equivalent", r" \u29E6 "),
    ("Implies", r" \uF523 "),
    ("RightTee", r" \u22A2 "),
    ("DoubleRightTee", r" \u22A8 "),
    ("LeftTee", r" \u22A3 "),
    ("DoubleLeftTee", r" \u2AE4 "),
    ("SuchThat", r" \u220D "),
    ("VerticalSeparator", r" \uF432 "),
    ("Therefore", r" \u2234 "),
    ("Because", r" \u2235 "),
    ("Backslash", r" \u2216 "),
]


literal_tokens = {
    "!": ["Unequal", "Factorial2", "Factorial"],
    '"': ["String"],
    "#": ["SlotSequence", "Slot"],
    "%": ["Out"],
    "&": ["And", "Function"],
    "'": ["Derivative"],
    "(": ["RawLeftParenthesis"],
    ")": ["RawRightParenthesis"],
    "*": ["NonCommutativeMultiply", "TimesBy", "Times"],
    "+": ["Increment", "AddTo", "Plus"],
    ",": ["RawComma"],
    "-": ["Decrement", "SubtractFrom", "Rule", "Minus"],
    ".": ["Number", "RepeatedNull", "Repeated", "Dot"],
    "/": [
        "MapAll",
        "Map",
        "DivideBy",
        "ReplaceRepeated",
        "ReplaceAll",
        "RightComposition",
        "Postfix",
        "TagSet",
        "Condition",
        "Divide",
    ],
    ":": ["MessageName", "RuleDelayed", "SetDelayed", "RawColon"],
    ";": ["Span", "Semicolon"],
    "<": [
        "RawLeftAssociation",
        "UndirectedEdge",
        "Get",
        "StringJoin",
        "LessEqual",
        "Less",
    ],
    "=": ["SameQ", "UnsameQ", "Equal", "Unset", "Set"],
    ">": ["PutAppend", "Put", "GreaterEqual", "Greater"],
    "?": ["Information", "PatternTest"],
    "@": ["ApplyList", "Apply", "Composition", "Prefix"],
    "[": ["RawLeftBracket"],
    "\\": [
        "LeftRowBox",
        "RightRowBox",
        "InterpretedBox",
        "SuperscriptBox",
        "SubscriptBox",
        "OverscriptBox",
        "UnderscriptBox",
        "OtherscriptBox",
        "FractionBox",
        "SqrtBox",
        "RadicalBox",
        "FormBox",
        "RawBackslash",
    ],
    "]": ["RawRightBracket"],
    "^": ["UpSetDelayed", "UpSet", "Power"],
    "_": ["Pattern"],
    "`": ["Pattern", "Symbol"],
    "|": ["RawRightAssociation", "Or", "Alternatives", "Function"],
    "{": ["RawLeftBrace"],
    "}": ["RawRightBrace"],
    "~": ["StringExpression", "Infix"],
}

for c in string.ascii_letters:
    literal_tokens[c] = ["Pattern", "Symbol"]

for c in string.digits:
    literal_tokens[c] = ["Number"]


def find_indices(literals: dict) -> dict:
    "find indices of literal tokens"

    literal_indices = {}
    for key, tags in literals.items():
        indices = []
        for tag in tags:
            for i, (tag2, _) in enumerate(tokens):
                if tag == tag2:
                    indices.append(i)
                    break
        assert len(indices) == len(
            tags
        ), f"problem matching tokens for symbol {key} having tags {tags}"
        literal_indices[key] = tuple(indices)
    return literal_indices


def compile_pattern(pattern):
    return re.compile(pattern, re.VERBOSE)


def compile_tokens(token_list):
    return [(tag, compile_pattern(pattern)) for tag, pattern in token_list]


filename_tokens = [("Filename", FILENAME_PATTERN)]

token_indices = find_indices(literal_tokens)
tokens = compile_tokens(tokens)
filename_tokens = compile_tokens(filename_tokens)
full_symbol_pattern_re: re.Pattern = compile_pattern(full_symbol_pattern_str)


def is_symbol_name(text: str) -> bool:
    """
    Returns ``True`` if ``text`` is a valid identifier. Otherwise returns
    ``False``.
    """
    # Can't we just call match here?
    return full_symbol_pattern_re.sub("", text) == ""


class Token:
    "A representation of a Wolfram Language token."

    def __init__(self, tag: str, text: str, pos: int):
        """
        :param tag: which type of token this is.
        :param text: The actual contents of the token.
        :param pos: The position of the token in the input feed.
        """
        self.tag = tag
        self.text = text
        self.pos = pos

    def __eq__(self, other):
        if not isinstance(other, Token):
            raise TypeError()
        return (
            self.tag == other.tag and self.text == other.text and self.pos == other.pos
        )

    def __repr__(self):
        return f"Token({self.tag}, {self.text}, {self.pos})"


class Tokeniser:
    """
    This converts input strings from a feeder and
    produces tokens of the Wolfram Language which can then be used in parsing.
    """

    modes = {"expr": (tokens, token_indices), "filename": (filename_tokens, {})}

    def __init__(self, feeder):
        """
        feeder: An instance of ``LineFeeder`` from which we receive
                input strings that are to be split up and put into tokens.
        """
        self.pos: int = 0
        self.feeder = feeder
        self.prescanner = Prescanner(feeder)
        self.code = self.prescanner.replace_escape_sequences()
        self.mode: str = "invalid"
        self._change_token_scanning_mode("expr")

    def _change_token_scanning_mode(self, mode: str):
        """
        Set the kinds of tokens that be will expected on the next token scan.
        See class variable "modes" above for the dictionary
        of token-scanning modes.
        """
        self.mode = mode
        self.tokens, self.token_indices = self.modes[mode]

    # TODO: Rename this to something that remotely makes sense?
    def incomplete(self):
        "Get more code from the prescanner and continue."
        self.prescanner.incomplete()
        self.code += self.prescanner.replace_escape_sequences()

    def sntx_message(self, pos: Optional[int] = None):
        """
        Send a "syntx{b,f} error message to the input-reading feeder.
        """
        if pos is None:
            pos = self.pos
        pre, post = self.code[:pos], self.code[pos:].rstrip("\n")
        if pos == 0:
            self.feeder.message("Syntax", "sntxb", post)
        else:
            self.feeder.message("Syntax", "sntxf", pre, post)

    # TODO: Convert this to __next__ in the future.
    def next(self) -> "Token":
        "Returns the next token."
        self._skip_blank()
        if self.pos >= len(self.code):
            return Token("END", "", len(self.code))

        # look for a matching pattern
        indices = self.token_indices.get(self.code[self.pos], ())
        match = None
        tag = "??invalid"
        if indices:
            for index in indices:
                tag, pattern = self.tokens[index]
                match = pattern.match(self.code, self.pos)
                if match is not None:
                    break
        else:
            for tag, pattern in self.tokens:
                match = pattern.match(self.code, self.pos)
                if match is not None:
                    break

        # no matching pattern found
        if match is None:
            self.sntx_message()
            raise ScanError()

        # custom tokenisation rules defined with t_tag
        override = getattr(self, "t_" + tag, None)
        if override is not None:
            return override(match)

        text = match.group(0)
        self.pos = match.end(0)
        return Token(tag, text, match.start(0))

    def _skip_blank(self):
        "Skip whitespace and comments"
        comment = []  # start positions of comments
        while True:
            if self.pos >= len(self.code):
                if comment:
                    try:
                        self.incomplete()
                    except ValueError:
                        # Funny symbols like | in comments can cause a ValueError.
                        # Until we have a better fix -- like noting we are inside a
                        # comment and should not try to substitute symbols -- ignore.
                        pass
                else:
                    break
            if comment:
                if self.code.startswith("(*", self.pos):
                    comment.append(self.pos)
                    self.pos += 2
                elif self.code.startswith("*)", self.pos):
                    comment.pop()
                    self.pos += 2
                else:
                    self.pos += 1
            elif self.code.startswith("(*", self.pos):
                comment.append(self.pos)
                self.pos += 2
            elif self.code[self.pos] in " \r\n\t":
                self.pos += 1
            else:
                break

    def _token_mode(self, match: re.Match, tag: str, mode: str) -> "Token":
        """
        Pick out the text in ``match``, convert that into a ``Token``, and
        return that.

        Also switch token-scanning mode.
        """
        text = match.group(0)
        self.pos = match.end(0)
        self._change_token_scanning_mode(mode)
        return Token(tag, text, match.start(0))

    def t_Filename(self, match: re.Match) -> "Token":
        "Scan for ``Filename`` token and return that"
        return self._token_mode(match, "Filename", "expr")

    def t_Get(self, match: re.Match) -> "Token":
        "Scan for a ``Get`` token from ``match`` and return that token"
        return self._token_mode(match, "Get", "filename")

    def t_Number(self, match: re.Match) -> "Token":
        "Break out from ``match`` the next token which is expected to be a Number"
        text = match.group(0)
        pos = match.end(0)
        if self.code[pos - 1 : pos + 1] == "..":
            # Trailing .. should be ignored. That is, `1..` is `Repeated[1]`.
            text = text[:-1]
            self.pos = pos - 1
        else:
            self.pos = pos
        return Token("Number", text, match.start(0))

    def t_Put(self, match: re.Match) -> "Token":
        "Scan for a ``Put`` token and return that"
        return self._token_mode(match, "Put", "filename")

    def t_PutAppend(self, match: re.Match) -> "Token":
        "Scan for a ``PutAppend`` token and return that"
        return self._token_mode(match, "PutAppend", "filename")

    def t_String(self, match: re.Match) -> "Token":
        "Break out from self.code the next token which is expected to be a String"
        start, end = self.pos, None
        self.pos += 1  # skip opening '"'
        newlines = []
        while True:
            if self.pos >= len(self.code):
                if end is None:
                    # reached end while still inside string
                    self.incomplete()
                    newlines.append(self.pos)
                else:
                    break
            char = self.code[self.pos]
            if char == '"':
                self.pos += 1
                end = self.pos
                break

            if char == "\\":
                self.pos += 2
            else:
                self.pos += 1

        indices = [start] + newlines + [end]
        result = "".join(
            self.code[indices[i] : indices[i + 1]] for i in range(len(indices) - 1)
        )
        return Token("String", result, start)
