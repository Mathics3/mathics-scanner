"""
Test precedences
================

Precedence values reported in the Mathics Scanner tables do not always match
with the values reported by `Precedence[...]` in WMA. As it was
pointed out by Robert L. Jacobson in
[https://www.robertjacobson.dev/posts/2018-09-03-generalizing-pemdas-what-is-an-operator/]
and [https://www.robertjacobson.dev/posts/2018-09-04-defining-the-wolfram-language-part-2-operator-properties/]

The behavior of the parser and the formatter of WMA do not always is consistent with the values
reported by `Precedence[...]`. Jacobson mentions that in the most of the cases, the behaviour is more
consistent with the values reported by `WolframLanguageData`, which are given following a different
numeric convention.

Some examples of these inconsistencies are:
* In WMA, `Precedence` reports the same value (215) for all the boolean operators
(`Not`, `And`, `Nand`,   `Xor`, `Or`, `Nor`) but behaves as
```
Precedence[Not]>Precedence[And]==Precedence[Nand]>Precedence[Xor]>Precedence[Or]==Precedence[Nor]
```

In other cases, precedence values of some operators are reported to be the default value (670)
while its behavior is different (Ej: `GreaterSlantEqual` and `LessSlantEqual` behaves as
their precedence were the same that the one for `LessEqual` and `GreaterEqual`).

In any case, the relevant information is the order relation that `Precedence` induce over the
operator and their associated symbols, and this is the information that we want to curate in
the MathicsScanner tables. 

This module test that the *order* induced by the precedence values assigned to each operator/symbol 
to be consistent with the one of a list built from WMA. This list was build by sorting the elements
according to their WMA `Precedence` values, and then modified in a way the ordering be consistent
with the way in which expressions involving these symbols / operators are parsed and formatter 
by `OutputForm`. This consistency was tested in WMA using the functions defined in
the `testprecedence.m` module.

Notice also that the tests of this module does not tries to check the behavior
of the parser or the formatters in Mathics-core, but just that the information
that MathicsScanner reports to be consistent with the behavior of WMA. 

"""

try:
    from test.mathics_helper import check_evaluation, evaluate, session

    MATHICS_NOT_INSTALLED = False
except ModuleNotFoundError:
    MATHICS_NOT_INSTALLED = True

import pytest


SYMBOLS_SORTED_BY_PRECEDENCE = [
    "CompoundExpression",
    "Put",
    "PutAppend",
    "Set",
    "SetDelayed",
    "UpSet",
    "UpSetDelayed",
    "Because",
    "Therefore",
    "Postfix",
    "Colon",
    "Function",
    "AddTo",
    "DivideBy",
    "SubtractFrom",
    "TimesBy",
    "ReplaceAll",
    "ReplaceRepeated",
    "RuleDelayed",
    "Rule",
    "Condition",
    "StringExpression",
    "Optional",
    "Alternatives",
    "Repeated",
    "RepeatedNull",
    "SuchThat",
    "DoubleLeftTee",
    "DoubleRightTee",
    "DownTee",
    "LeftTee",
    "Perpendicular",  # 190
    "RightTee",  # 190
    # In WMA, `RoundImplies` has a
    # larger precedence value (240) than Not (230),
    # but behaves as it has a precedence
    # between RightTee and UpTee, both with
    # a precedence value of 190.
    #
    # This behavior is not the one in Mathics. For example,
    # the input
    # a\[RoundImplies]b\[UpTee]c//FullForm
    # Is parsed in WMA as
    # RoundImplies[a,UpTee[b,c]],
    # But in Mathics as
    # UpTee[RoundImplies[a, b], c]
    #    "RoundImplies", # WMA->240, Mathics->200, Must be ~193
    "UpTee",  # 190   Must be ~197
    "Implies",  # 200
    "Equivalent",
    "Nor",
    "Or",
    "Xor",
    "And",
    "Nand",
    "Not",
    "NotReverseElement",
    "NotSquareSubsetEqual",
    "NotSquareSupersetEqual",
    "NotSubset",
    "NotSubsetEqual",
    "NotSuperset",
    "NotSupersetEqual",
    "ReverseElement",
    "SquareSubset",
    "SquareSubsetEqual",
    "SquareSuperset",
    "SquareSupersetEqual",
    "Subset",
    "SubsetEqual",
    "Superset",
    "SupersetEqual",
    "DoubleLeftArrow",
    "DoubleLeftRightArrow",
    "DoubleRightArrow",
    "DownLeftRightVector",
    "DownLeftTeeVector",
    "DownLeftVector",
    "DownLeftVectorBar",
    "DownRightTeeVector",
    "DownRightVector",
    "DownRightVectorBar",
    "LeftArrow",
    "LeftArrowBar",
    "LeftArrowRightArrow",
    "LeftRightArrow",
    "LeftRightVector",
    "LeftTeeArrow",
    "LeftTeeVector",
    "LeftVector",
    "LeftVectorBar",
    "LowerLeftArrow",
    "LowerRightArrow",
    "RightArrow",
    "RightArrowBar",
    "RightArrowLeftArrow",
    "RightTeeArrow",
    "RightTeeVector",
    "RightVector",
    "RightVectorBar",
    "ShortLeftArrow",
    "ShortRightArrow",
    "UpperLeftArrow",
    "UpperRightArrow",
    "DoubleVerticalBar",
    "NotDoubleVerticalBar",
    "VerticalBar",
    "Equal",
    "Greater",
    "GreaterEqual",
    "Less",
    "LessEqual",
    "GreaterSlantEqual",
    "LessSlantEqual",
    "SameQ",
    "Unequal",
    "UnsameQ",
    "Congruent",
    "CupCap",
    "DotEqual",
    "EqualTilde",
    "Equilibrium",
    "GreaterEqualLess",
    "GreaterFullEqual",
    "GreaterGreater",
    "GreaterLess",
    "GreaterTilde",
    "HumpDownHump",
    "HumpEqual",
    "LeftTriangle",
    "LeftTriangleBar",
    "LeftTriangleEqual",
    "LessEqualGreater",
    "LessFullEqual",
    "LessGreater",
    "LessLess",
    "LessTilde",
    "NestedGreaterGreater",
    "NestedLessLess",
    "NotCongruent",
    "NotCupCap",
    "NotGreater",
    "NotGreaterEqual",
    "NotGreaterFullEqual",
    "NotGreaterLess",
    "NotGreaterTilde",
    "NotLeftTriangle",
    "NotLeftTriangleEqual",
    "NotLess",
    "NotLessEqual",
    "NotLessFullEqual",
    "NotLessGreater",
    "NotLessTilde",
    "NotPrecedes",
    "NotPrecedesSlantEqual",
    "NotPrecedesTilde",
    "NotRightTriangle",
    "NotRightTriangleEqual",
    "NotSucceeds",
    "NotSucceedsSlantEqual",
    "NotSucceedsTilde",
    "NotTilde",
    "NotTildeEqual",
    "NotTildeFullEqual",
    "NotTildeTilde",
    "Precedes",
    "PrecedesEqual",
    "PrecedesSlantEqual",
    "PrecedesTilde",
    "Proportion",
    "Proportional",
    "ReverseEquilibrium",
    "RightTriangle",
    "RightTriangleBar",
    "RightTriangleEqual",
    "Succeeds",
    "SucceedsEqual",
    "SucceedsSlantEqual",
    "SucceedsTilde",
    "Tilde",
    "TildeEqual",
    "TildeFullEqual",
    "TildeTilde",
    "DirectedEdge",
    "UndirectedEdge",
    "SquareUnion",
    "UnionPlus",
    "Span",
    "SquareIntersection",
    "MinusPlus",
    "PlusMinus",
    "Plus",
    "Subtract",  #  310
    #    "Integrate", # In Mathics, this has the default precedence. In WMA, 325
    "CircleMinus",  # 330
    "CirclePlus",
    "Cup",
    "Cap",
    "Coproduct",
    "VerticalTilde",
    "Star",
    "Times",
    "CenterDot",
    "CircleTimes",
    "Vee",
    "Wedge",
    "Diamond",
    "Backslash",
    "Divide",
    "Minus",
    "Dot",
    "CircleDot",
    "SmallCircle",
    "Square",  # 540
    "Del",  # In WMA, has the same precedence as DifferentialD and CapitalDifferentialD
    "CapitalDifferentialD",  # Mathics 560, WMA 550
    "DifferentialD",  # Mathics 560, WMA, 550
    "DoubleDownArrow",  # 580
    "DoubleLongLeftArrow",
    "DoubleLongLeftRightArrow",
    "DoubleLongRightArrow",
    "DoubleUpArrow",
    "DoubleUpDownArrow",
    "DownArrow",
    "DownArrowBar",
    "DownArrowUpArrow",
    "DownTeeArrow",
    "LeftDownTeeVector",
    "LeftDownVector",
    "LeftDownVectorBar",
    "LeftUpDownVector",
    "LeftUpTeeVector",
    "LeftUpVector",
    "LeftUpVectorBar",
    "LongLeftArrow",
    "LongLeftRightArrow",
    "LongRightArrow",
    "ReverseUpEquilibrium",
    "RightDownTeeVector",
    "RightDownVector",
    "RightDownVectorBar",
    "RightUpDownVector",
    "RightUpTeeVector",
    "RightUpVector",
    "RightUpVectorBar",
    "ShortDownArrow",
    "ShortUpArrow",
    "UpArrow",
    "UpArrowBar",
    "UpArrowDownArrow",
    "UpDownArrow",
    "UpEquilibrium",
    "UpTeeArrow",
    "Power",
    "StringJoin",
    "Factorial",
    "Factorial2",
    "Apply",
    "Map",
    "MapApply",  # In WMA, the default precedence (670) is reported
    "Prefix",
    "Decrement",
    "Increment",
    "PreDecrement",
    "PreIncrement",
    "Unset",
    "Derivative",
    "PatternTest",
    "Get",
    "MessageName",
    "Information",
]


# TODO: rewrite this test by reading the table directly.
@pytest.mark.skipif(MATHICS_NOT_INSTALLED, reason="Requires Mathics-core installed")
def test_precedence_order():
    """
    Test the precedence order.

    This test checks that the precedence values of the symbols associted
    to WL operators follows the order required to make the
    that the parser and the OutputForm formatter produce
    outputs consistent with the WMA behavior.
    """
    precedence_values = [
        session.evaluate(f"Precedence[{symbol}]").value
        for symbol in SYMBOLS_SORTED_BY_PRECEDENCE
    ]
    fails = []
    for i in range(len(precedence_values) - 1):
        if precedence_values[i] > precedence_values[i + 1]:
            fails.append(
                f"Precedence[{SYMBOLS_SORTED_BY_PRECEDENCE[i]}]={precedence_values[i]}>"
                f"{precedence_values[i+1]}=Precedence[{SYMBOLS_SORTED_BY_PRECEDENCE[i+1]}]"
            )
    for fail in fails:
        print(fail)
    assert len(fails) == 0
