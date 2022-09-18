# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_ascii():
    ascii_operator_to_name = json_data["ascii-operator-to-name"]
    ascii_operators = json_data["ascii-operators"]
    operator_keys = frozenset(ascii_operator_to_name.keys())
    # operator_to_precedence = json_data["operator-to-precedence"]
    for chars in json_data["ascii-operators"]:
        assert chars in ascii_operators
        assert chars in operator_keys
        # assert chars in unicode_to_operator.keys()
        name = ascii_operator_to_name.get(chars)
        assert name is not None
        assert name.startswith(r"\[")
        assert name.endswith(r"]")
        raw_name = name[len(r"\[") : -len(r"]")]
        assert raw_name in yaml_data
