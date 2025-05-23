# -*- coding: utf-8 -*-

import re
import unicodedata

from mathics_scanner.load import load_mathics_character_yaml

yaml_data = load_mathics_character_yaml()


def check_attr_is_invertible(attr: str):
    for v in yaml_data.values():
        if attr in v:
            attr_v = v[attr]

            if attr_v in ["|"]:
                continue

            attr_vs = [c for c, v in yaml_data.items() if v.get(attr) == attr_v]

            assert (
                len(attr_vs) == 1
            ), f"{attr_vs} all have the same {attr} field set to {attr_v}"


def check_has_attr(attr: str):
    for k, v in yaml_data.items():
        assert attr in v, f"{k} has no {attr} attribute"


def test_yaml_field_names():
    for k, v in yaml_data.items():
        diff = set(v.keys()) - {
            "amslatex",
            "ascii",
            "esc-alias",
            "has-unicode-inverse",
            "is-builtin-constant",
            "is-letter-like",
            "operator-name",
            "precedence",
            "unicode-equivalent",
            "unicode-equivalent-name",
            "unicode-reference",
            "wl-reference",
            "wl-unicode",
            "wl-unicode-name",
        }
        assert diff == set(), f"Item {k} has unknown fields {diff}"


def test_amslatex():
    amslatex_seen = set()
    dup_amslatex = set(["\\Rightarrow", "\\rightarrow", "\\uparrow"])
    for k, v in yaml_data.items():
        a = v.get("amslatex", None)
        if a is None:
            continue
        msg_prefix = f"In {k} with amslatex {a}, "
        if a.startswith("$"):
            assert a.endswith("$"), (
                msg_prefix + "if something starts in math mode, it must end with '$'"
            )
        if a.endswith("$"):
            assert a.startswith("$"), (
                msg_prefix + "if something ends in math mode, it must start with '$'"
            )
        if a in dup_amslatex:
            continue
        # There is nothing wrong in having two characters with the same
        # amslatex representation:
        # assert a not in amslatex_seen, msg_prefix + "value seen before"
        # amslatex_seen.add(a)


def test_operators():
    ascii_seen = set()
    operator_name_seen = set()

    # These names have more than one operator symbol
    dup_operators = set(["Apply", "Function", "MapApply", "LeftList"])

    # These symbols have more than one operator name
    dup_operator_symbols = set(["?", "!"])

    for k, v in yaml_data.items():
        if "ascii" in v:
            if len(v["ascii"]) > 1:
                assert (
                    "operator-name" in v
                ), f"In {k}: ASCII with more than one characters must be an operator"
                pass
        else:
            assert (
                "wl-unicode" in v
            ), f"In {k}: there must be either an ascii name or have a wl-unicode"
        if "operator-name" not in v:
            continue

        assert not v["is-letter-like"], f'Operator "{k}" should not be letter-like'

        if "ascii" in v:
            ascii = v["ascii"]
            if ascii in dup_operator_symbols:
                ascii_seen.add(ascii)
                continue
            assert ascii not in ascii_seen

        operator_name = v["operator-name"]
        if operator_name in dup_operators:
            continue
        assert (
            operator_name not in operator_name_seen
        ), f"Operator name {operator_name} has operator {k} already been seen"
        operator_name_seen.add(operator_name)


def test_precedence():
    for k, v in yaml_data.items():
        if "precedence" in v:
            p = v.get("precedence", None)
            msg_prefix = f"In {k} with precedence {p}, "
            assert isinstance(p, int), msg_prefix + "must be an integer"
            assert p >= 0, msg_prefix + "must be a positive integer"
            assert "operator-name" in v, msg_prefix + "must have an operator name"


def test_unicode_name():
    for k, v in yaml_data.items():
        # Hack to skip characters that are correct but that doesn't show up in
        # unicodedata.name
        if "unicode-equivalent-name" not in v:
            continue

        if "unicode-equivalent" in v:
            uni = v["unicode-equivalent"]

            try:
                expected_name = " + ".join(unicodedata.name(c) for c in uni)
            except ValueError:
                raise ValueError(
                    f"{k}'s unicode-equivalent doesn't have a unicode name (it's not valid unicode)"
                )

            real_name = v.get("unicode-equivalent-name")

            if real_name is None:
                raise ValueError(
                    "{k} has a unicode equivalent but doesn't have the unicode-equivalent-name field"
                )

            if k == "VerticalBar":
                continue
            assert real_name == expected_name or expected_name.startswith(
                "MODIFIER LETTER SMALL SCHWA"
            ), f"{k} has unicode-equivalent-name set to {real_name} but it should be {expected_name}"
        else:
            assert (
                "ascii" in v
            ), f"{k} has unicode-equivalent-name set to {v['unicode-equivalent-name']} but it doesn't have a unicode or ascii equivalent"


def test_wl_unicode():
    for k, v in yaml_data.items():
        if "operator-name" in v:
            if "ascii" in v:
                # Operators like "**" or "?" don't need to
                # have a wl-unicode equivalent and might not have a
                # unique equivalent
                continue
        assert (
            "wl-unicode" in v or "unicode-equivalent" in v or "ascii" in v
        ), f"{k} has neither wl-unicode, unicode-equivalent, nor ascii attribute"


def test_unicode_operators():
    exclude_list = frozenset(
        """Apply3Ats LeftDoubleBracket Function FunctionAmpersand NotEqual RawGreater RawLeftBrace RightDoubleBracket""".split(
            " "
        )
    )
    for k, v in yaml_data.items():
        if k in exclude_list:
            continue
        if "operator-name" not in v:
            continue
        operator_name = v["operator-name"]
        assert (
            k == operator_name
        ), f"Section name {k} should match operator-name {operator_name} or be explicitly excluded when a section has an operator"


def test_wl_unicode_name():
    for k, v in yaml_data.items():
        if "wl-unicode" not in v:
            continue
        wl = v["wl-unicode"]

        try:
            expected_name = unicodedata.name(wl)
        except (ValueError, TypeError):
            continue

        real_name = v.get("wl-unicode-name")

        if real_name is None:
            raise ValueError(f"Section {k}'s wl-unicode has a name but it isn't listed")

        assert (
            real_name == expected_name
        ), f"Section {k} has wl-unicode-name set to {real_name} but it should be {expected_name}"


def test_general_yaml_sanity():
    # Check if required attributes are in place
    check_has_attr("is-letter-like")
    check_has_attr("has-unicode-inverse")

    # Check if attributes that should be invertible are in fact invertible
    check_attr_is_invertible("wl-unicode")
    check_attr_is_invertible("esc-alias")


def test_is_letter_like():
    letter_pat = re.compile(r"(?u)^[^\W_0-9]$")
    for k, v in yaml_data.items():
        if "unicode-equivalent" in v:
            is_letter_like = bool(letter_pat.match(v["unicode-equivalent"]))
            if "is-letter-like" not in v:
                print(f"{k} needs is-letter-like: {bool(is_letter_like)}")
            elif v["is-letter-like"] != is_letter_like:
                print(f"{k} is-letter-like should be: {bool(is_letter_like)}")
