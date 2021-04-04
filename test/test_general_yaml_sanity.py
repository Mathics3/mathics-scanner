# -*- coding: utf-8 -*-

from mathics_scanner.load import load_mathics_character_yaml
import unicodedata

yaml_data = load_mathics_character_yaml()


def check_attr_is_invertible(attr: str):
    for v in yaml_data.values():
        if attr in v:
            attr_v = v[attr]

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
            "ascii",
            "esc-alias",
            "has-unicode-inverse",
            "is-letter-like",
            "operator-name",
            "unicode-equivalent",
            "unicode-equivalent-name",
            "wl-unicode",
            "wl-unicode-name",
        }
        assert diff == set(), f"Item {k} has unknown fields {diff}"


def test_operators():
    ascii_seen = set()
    operator_name_seen = set()
    dup_operators = set(["Apply", "Function"])
    for k, v in yaml_data.items():
        if "ascii" in v:
            if len(v["ascii"]) > 1:
                assert (
                    "operator-name" in v
                ), "In %s: ASCII with more than one characters must be an operator" % (
                    k
                )
                pass
        else:
            assert "wl-unicode" in v, (
                "In %s: there must be either an ascii name or have a wl-unicode" % k
            )
        if "operator-name" not in v:
            continue

        assert not v["is-letter-like"], "Operator %s should not be letter-like" % k

        assert "ascii" in v, 'Operator %s should have an "ascii" field' % k
        ascii = v["ascii"]
        assert ascii not in ascii_seen
        ascii_seen.add(ascii)

        operator_name = v["operator-name"]
        if operator_name in dup_operators:
            continue
        assert (
            operator_name not in operator_name_seen
        ), "Operator name %s has operator %s already been seen" % (operator_name, k)
        operator_name_seen.add(operator_name)


def test_wl_unicode_name():
    for k, v in yaml_data.items():
        if "wl-unicode" not in v:
            continue
        wl = v["wl-unicode"]

        try:
            expected_name = unicodedata.name(wl)
        except ValueError:
            continue

        real_name = v.get("wl-unicode-name")

        if real_name is None:
            raise ValueError("{k}'s wl-unicode has a name but it isn't listed")

        assert (
            real_name == expected_name
        ), f"{k} has wl-unicode-name set to {real_name} but it should be {expected_name}"


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
                import pdb

                pdb.set_trace()
                raise ValueError(
                    f"{k}'s unicode-equivalent doesn't have a unicode name (it's not valid unicode)"
                )

            real_name = v.get("unicode-equivalent-name")

            if real_name is None:
                raise ValueError(
                    "{k} has a unicode equivalent but doesn't have the unicode-equivalent-name field"
                )

            assert (
                real_name == expected_name
            ), f"{k} has wl-unicode-name set to {real_name} but it should be {expected_name}"
        else:
            assert (
                "unicode-equivalent-name" not in v
            ), f"{k} has unicode-equivalent-name set to {v['unicode-equivalent-name']} but it doesn't have a unicode equivalent"


def test_wl_unicode():
    for k, v in yaml_data.items():
        if "operator-name" in v:
            if "ascii" in v:
                # Operators like "**" or "?" don't need to
                # have a wl-unicode equivalent and might not have a
                # unique equivalent
                continue
        assert (
            "wl-unicode" in v or "unicode-equivalent" in v
        ), f"{k} has neither wl-unicode nor unicode-equivalent attribute"


def test_general_yaml_sanity():
    # Check if required attributes are in place
    check_has_attr("is-letter-like")
    check_has_attr("has-unicode-inverse")

    # Check if attributes that should be invertible are in fact invertible
    check_attr_is_invertible("wl-unicode")
    check_attr_is_invertible("esc-alias")
