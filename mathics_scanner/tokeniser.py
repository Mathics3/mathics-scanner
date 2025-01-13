"""
Tokenizer functions
"""

import os.path as osp
import re
import string
from typing import Dict, List, Optional, Tuple

from mathics_scanner.characters import _letterlikes, _letters
from mathics_scanner.errors import ScanError
from mathics_scanner.prescanner import Prescanner

try:
    import ujson
except ImportError:
    import json as ujson  # type: ignore[no-redef]


OPERATOR_DATA = {}
ROOT_DIR = osp.dirname(__file__)
OPERATORS_TABLE_PATH = osp.join(ROOT_DIR, "data", "operators.json")


FILENAME_TOKENS: List = []
TOKENS: List[Tuple] = []
TOKEN_INDICES: Dict = {}


# special patterns
NUMBER_PATTERN = r"""
( (?# Two possible forms depending on whether base is specified)
    (\d+\^\^([a-zA-Z0-9]+\.?[a-zA-Z0-9]*|[a-zA-Z0-9]*\.?[a-zA-Z0-9]+))
    | (\d+\.?\d*|\d*\.?\d+)
)
(``?(\+|-)?(\d+\.?\d*|\d*\.?\d+)|`)?        (?# Precision / Accuracy)
(\*\^(\+|-)?\d+)?                           (?# Exponent)
"""

# TODO: Check what of this should be a part of the module interface.
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

# FIXME incorportate the below table in to Function/Operators YAML
# Table of correspondneces between a Mathics3 token name (or "tag")
# and WMA CodeTokenize name
MATHICS3_TAG_TO_CODETOKENIZE: Dict[str, str] = {
    "AddTo": "PlusEqual",
    "Alternatives": "Bar",
    "And": "AmpAmp",
    "Apply": "AtAt",
    "ApplyList": "AtAtAt",
    "Cap": "LongName`Cap",
    "Cup": "LongName`Cup",
    "Decrement": "MinusMinus",
    "Divide": "Slash",
    "DivideBy": "SlashEqual",
    "Equal": "EqualEqual",
    "Factorial": "Bang",
    "Factorial2": "BangBang",
    "Function": "Amp",
    "Get": "LessLess",
    "Increment": "PlusPlus",
    "Infix": "Tilde",
    "Information": "QuesionQuestion",
    "InterpretedBox": "LinearSequence`Bang",
    "MessageName": "ColonColon",
    "Or": "BarBar",
    "Pattern": "Under",
    "PatternTest": "Question",
    "Postfix": "SlashSlash",
    "Prefix": "At",
    "Put": "GreaterGreater",
    "RawComma": "Comma",
    "RawLeftAssociation": "LessBar",
    "RawLeftBrace": "OpenCurly",
    "RawLeftBracket": "OpenSquare",
    "RawRightAssociation": "BarGreater",
    "RawRightBrace": "CloseCurly",
    "RawRightBracket": "CloseSquare",
    "RightRowBox": "CloseParen",
    "Rule": "MinusGreater",
    "RuleDelayed": "ColonGreater",
    "ReplaceAll": "SlashDot",
    "ReplaceRepeated": "SlashSlashDot",
    "SameQ": "EqualEqualEqual",
    "Set": "Equal",
    "SetDelayed": "ColonEqual",
    "Slot": "Hash",
    "SlotSequence": "HashHash",
    "SubtractFrom": "MinusEqual",
    "Times": "Star",
    "TimesBy": "StarEqual",
    "Unequal": "BangEqual",
}


def compile_pattern(pattern):
    """Compile a pattern from a regular expression"""
    return re.compile(pattern, re.VERBOSE)


def init_module():
    """
    Initialize the module using the information
    stored in the JSON tables.
    """
    # Load Mathics3 character information from JSON. The JSON is built from
    # named-characters.yml

    if not osp.exists(OPERATORS_TABLE_PATH):
        print(
            "Warning: Mathics3 Operator information are missing; "
            f"expected to be in {OPERATORS_TABLE_PATH}"
        )
        print(
            "Please run the " "mathics_scanner/generate/build_operator_tables.py script"
        )
        return

    with open(osp.join(OPERATORS_TABLE_PATH), "r", encoding="utf8") as operator_f:
        OPERATOR_DATA.update(ujson.load(operator_f))

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
        # FIXME: we should be able to get this from JSON.
        # Something prevents us from matching up operators here though.
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
        ("GreaterEqual", r" (\>\=) | \u2265 "),
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
        # allow whitespace but avoid e.g. x=.01
        ("Unset", r" \=\s*\.(?!\d|\.) "),
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
        ("Function", r" \& | \uF4A1 | \u27FC | \|-> "),
        ("RawColon", r" \: "),
        # ('DiscreteShift', r' \uf4a3 '),
        # ('DiscreteRatio', r' \uf4a4 '),
        # ('DifferenceDelta', r' \u2206 '),
        # ('PartialD', r' \u2202 '),
        # uf4a0 is Wolfram custom, u2a2f is standard unicode
        ("Cross", r" \uf4a0 | \u2a2f"),
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
        # ('Sum', r' \u2211 '),
        # ('Product', r' \u220f '),
        ("Nor", r" \u22BD "),
        ("Nand", r" \u22BC "),
        ("Xor", r" \u22BB "),
        ("Xnor", r" \uF4A2 "),
        ("Intersection", r" \u22c2 "),
        ("Union", r" \u22c3 "),
        ("Element", r" \u2208 "),
        ("NotElement", r" \u2209 "),
        ("ForAll", r" \u2200 "),
        ("Exists", r" \u2203 "),
        ("NotExists", r" \u2204 "),
        ("Not", r" \u00AC "),
        ("Equivalent", r" \u29E6 "),
        ("Implies", r" \uF523 "),
        ("VerticalSeparator", r" \uF432 "),
    ]

    for table_name in ("box-operators", "no-meaning-infix-operators"):
        table_info = OPERATOR_DATA[table_name]
        for operator_name, unicode in table_info.items():
            # if any([tup[0] == operator_name for tup in tokens]):
            #     print(f"Please remove {operator_name}")

            # Ternary operators have two character symbols
            # in a list. For tokens, we just want the first
            # of the pair
            if isinstance(unicode, list):
                unicode = unicode[0]
            tokens.append((operator_name, rf" {unicode} "))

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

    filename_tokens = [("Filename", FILENAME_PATTERN)]

    # Reset the global variables
    TOKENS.clear()
    TOKEN_INDICES.clear()
    FILENAME_TOKENS.clear()

    TOKENS.extend(compile_tokens(tokens))
    TOKEN_INDICES.update(find_indices(literal_tokens))
    FILENAME_TOKENS.extend(compile_tokens(filename_tokens))


def find_indices(literals: dict) -> dict:
    "find indices of literal tokens"

    literal_indices = {}
    for key, tags in literals.items():
        indices = []
        for tag in tags:
            for i, (tag2, _) in enumerate(TOKENS):
                if tag == tag2:
                    indices.append(i)
                    break
        assert len(indices) == len(
            tags
        ), f"problem matching tokens for symbol {key} having tags {tags}"
        literal_indices[key] = tuple(indices)
    return literal_indices


def compile_tokens(token_list):
    """Compile a list of tokens into a list
    of tuples of the form (tag, compiled_pattern)"""
    return [(tag, compile_pattern(pattern)) for tag, pattern in token_list]


FULL_SYMBOL_PATTERN_RE: re.Pattern = compile_pattern(full_symbol_pattern_str)


def is_symbol_name(text: str) -> bool:
    """
    Returns ``True`` if ``text`` is a valid identifier. Otherwise returns
    ``False``.
    """
    # Can't we just call match here?
    return FULL_SYMBOL_PATTERN_RE.sub("", text) == ""


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

    def __repr__(self) -> str:
        return f"Token({repr(self.tag)}, {repr(self.text)}, {self.pos})"

    @property
    def code_tokenize_format(self) -> str:
        """
        Format token more like the way CodeTokenize of CodeParser does.
        """
        token_name = MATHICS3_TAG_TO_CODETOKENIZE.get(self.tag, self.tag)
        if token_name not in ("String", "Symbol"):
            token_name = f"Token`{token_name}"
        return f"LeafNode[{token_name}, {repr(self.text)}, {self.pos}]"


class Tokeniser:
    """
    This converts input strings from a feeder and
    produces tokens of the Wolfram Language which can then be used in parsing.
    """

    # TODO: Check if this dict should be updated using the init_module function
    modes = {"expr": (TOKENS, TOKEN_INDICES), "filename": (FILENAME_TOKENS, {})}

    def __init__(self, feeder):
        """
        feeder: An instance of ``LineFeeder`` from which we receive
                input strings that are to be split up and put into tokens.
        """
        assert len(TOKENS) > 0, (
            "Tokenizer was not initialized. "
            f"Check if {OPERATORS_TABLE_PATH} "
            "is available"
        )
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
    def next(self) -> Token:
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
                        # `incomplete` tries to parse substrings like `\|AAAAA`
                        # that can be interpreted as a character reference.
                        # To do that, it tries to get the
                        # new line using the method
                        # `Prescanner.replace_escape_sequences()`
                        # Inside a comment, the special meaning of escape sequences
                        # like `\|` should not be taken into account.
                        #
                        # In case of error, just let's pick the code
                        # from the `input_line` attribute of
                        # prescanner:
                        self.code = self.prescanner.input_line
                        # TODO: handle the corner case where the rest of the line
                        # include escaped sequences, out of the comment.
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

    def _token_mode(self, match: re.Match, tag: str, mode: str) -> Token:
        """
        Pick out the text in ``match``, convert that into a ``Token``, and
        return that.

        Also switch token-scanning mode.
        """
        text = match.group(0)
        self.pos = match.end(0)
        self._change_token_scanning_mode(mode)
        return Token(tag, text, match.start(0))

    def t_Filename(self, match: re.Match) -> Token:
        "Scan for ``Filename`` token and return that"
        return self._token_mode(match, "Filename", "expr")

    def t_Get(self, match: re.Match) -> Token:
        "Scan for a ``Get`` token from ``match`` and return that token"
        return self._token_mode(match, "Get", "filename")

    def t_Number(self, match: re.Match) -> Token:
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

    def t_Put(self, match: re.Match) -> Token:
        "Scan for a ``Put`` token and return that"
        return self._token_mode(match, "Put", "filename")

    def t_PutAppend(self, match: re.Match) -> Token:
        "Scan for a ``PutAppend`` token and return that"
        return self._token_mode(match, "PutAppend", "filename")

    def t_String(self, match: re.Match) -> Token:
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


# Call the function that initializes the dictionaries.
# If the JSON tables were modified during the execution,
# just call this function again.
init_module()
