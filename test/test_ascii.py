# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_ascii():
    ascii_operator_to_character_symbol = json_data["ascii-operator-to-character-symbol"]
    ascii_operator_to_symbol = json_data["ascii-operator-to-symbol"]
    ascii_operators = json_data["ascii-operators"]
    operator_keys = frozenset(ascii_operator_to_symbol.keys())
    # operator_to_precedence = json_data["operator-to-precedence"]
    for chars in json_data["ascii-operators"]:
        assert chars in ascii_operators
        assert chars in operator_keys
        # assert chars in unicode_to_operator.keys()
        char_symbol = ascii_operator_to_character_symbol.get(chars)
        assert char_symbol is not None
        assert char_symbol.startswith(r"\[")
        assert char_symbol.endswith(r"]")
        raw_char_symbol = char_symbol[len(r"\[") : -len(r"]")]
        assert raw_char_symbol in yaml_data
        assert raw_char_symbol in ascii_operator_to_symbol.values()
