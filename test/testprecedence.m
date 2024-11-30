
PrecedenceOrderByParsing::usage="`PrecedenceOrderByParsing[op1, op2]`  \
Evaluates the precedence ordering of two operators, according the way they are parsed. 1 if op1 has lower precedence than op2,
0 if they are equal and -1 if op2 has lower precedence than op1. If order cannot be determined, return None.
"

CheckPrecedenceOutput::usage="`CheckPrecedenceOutput[op]`\ checks if the Precedence value reported by `Precedence[op]` is \
consistent with the way in which expressions involving `op` are formatted when are inside an `Infix` expression."


BeginPackage["testprecedences`"];


(*Check the order of the precedence for two operators
by looking how are they parsed.
*)
PrecedenceOrderByParsing[op1_String, op2_String] := 
 Module[{a, b, c, h1, h2, hl, hr, testexpr},
  h1 = ToExpression["a" <> op1 <> "b"][[0]]; 
  h2 = ToExpression["a" <> op2 <> "b"][[0]];
  hl = Head[ToExpression["a" <> op1 <> "b" <> op2 <> "c"]];
  hr = Head[ToExpression["a" <> op2 <> "b" <> op1 <> "c"]];
  If[hl === hr, Return[If[hl === h1, 1, If[hl === h2, -1, None]]], 
   Return[0]]
  ]


(*Check if the OutputForm is consistent with the precedence*)
CheckPrecedenceOutput[op_String] := 
 Module[{a, b, c, precedence, testexpr, test, lesseq, largeeq},
  testexpr = ToExpression["b" <> op <> "c"]; 
  precedence = IntegerPart[Precedence[Head[testexpr]]];
  test = ToString[Infix[{a, testexpr}, "~", precedence - 1, None], 
    OutputForm];
  If[StringPart[test, -1] == ")", Return[False]];
  test = ToString[Infix[{a, testexpr}, "~", precedence, None], 
    OutputForm];
  If[StringPart[test, -1] != ")", Return[False]];
  test = ToString[Infix[{a, testexpr}, "~", precedence + 1, None], 
    OutputForm];
  If[StringPart[test, -1] != ")", Return[False]];
  test = ToString[Infix[{testexpr, a}, "~", precedence - 1, None], 
    OutputForm];
  If[StringPart[test, 1] == "(", Return[False]];
  test = ToString[Infix[{testexpr, a}, "~", precedence, None], 
    OutputForm];
  If[StringPart[test, 1] != "(", Return[False]];
  test = ToString[Infix[{testexpr, a}, "~", precedence + 1, None], 
    OutputForm];
  If[StringPart[test, 1] != "(", Return[False]];
  True
  ]

EndPackage[]