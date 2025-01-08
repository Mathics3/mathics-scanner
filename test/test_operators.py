# -*- coding: utf-8 -*-
"""
Test contents of mathics_scanner/data/operators.yml file
"""
import os.path as osp
from pathlib import Path

import yaml

data_dir = Path(osp.normpath(osp.dirname(__file__)), "..", "mathics_scanner", "data")
with open(data_dir / "operators.yml", "r", encoding="utf8") as operator_f, open(
    data_dir / "named-characters.yml", "r", encoding="utf8"
) as character_f:
    # Load the YAML data.
    operator_data = yaml.load(operator_f, Loader=yaml.FullLoader)
    character_data = yaml.load(character_f, Loader=yaml.FullLoader)

operator_names = set(tuple(operator_data.keys()))


def test_associativity_field():
    """
    Check "associativity" field is one of the accepted values,
      None, "left", "non-associative", "right", or "unknown"
    """
    associativity_set = {None, "left", "non-associative", "right", "unknown"}
    for operator_name, operator_info in operator_data.items():
        assert operator_info["associativity"] in associativity_set, (
            f"operator {operator_name} associativity is {operator_info['associativity']}; "
        ) + f"should be one of: {associativity_set}; "


def test_operators():
    # We need to use "operator-name" instead of YAML "name" key
    # because of situations like "FunctionAmpersand"
    # which is the same as "Function", but "Function" is already
    # needed/used as a YAML key. Apply3Ats (MapApply) is another
    # example.
    character_operator_names = set(
        [
            value["operator-name"]
            for value in operator_data.values()
            if "operator-name" in value
        ]
    )

    left_character_operators = {
        operator_name
        for operator_name in character_operator_names
        if operator_name.startswith("Left")
    }
    right_character_operators = {
        operator_name
        for operator_name in character_operator_names
        if operator_name.startswith("Right")
    }

    # For "Left" operators listed in name characters, check that there is a corresponding "Right"
    # and check that the name without "Left" or "Right" appears in the operator table.
    left_operator_remove = set()
    for left_operator in left_character_operators:
        if left_operator in operator_names:
            continue
        operator_name = left_operator[len("Left") :]
        right_operator = "Right" + operator_name
        assert right_operator in right_character_operators
        assert operator_name in operator_names
        # print(f"WOOT short found: {operator_name}")
        left_operator_remove.add(left_operator)

    right_operator_remove = set()
    for right_operator in right_character_operators:
        if right_operator in operator_names:
            continue
        operator_name = right_operator[len("Right") :]
        left_operator = "Left" + operator_name
        assert left_operator in left_character_operators
        character_operator_names.remove(right_operator)
        assert operator_name in operator_names
        operator_names.remove(operator_name)
        right_operator_remove.add(right_operator)

    character_operator_names -= left_operator_remove
    character_operator_names -= right_operator_remove

    # For some reason we decided to exclude "Prefix" as a character operator. Add it back in here
    character_operator_names.add("Prefix")

    extra_character_operators = character_operator_names - operator_names

    # FIXME: go over tables to make the below work
    # extra_operator_names = operator_names - character_operator_names
    # assert not extra_operator_names, f"Should not have extra operators in YAML operator table {extra_operator_names}"

    assert (
        not extra_character_operators
    ), f"Should not have extra operators in JSON character table {extra_character_operators}"


def test_meaningful_field():
    """
    Check that all operators where the "meaningful" field is "false" have an valid affix value.
    """
    for operator_name, operator_info in operator_data.items():
        if operator_info.get("meaningful", True) is False and (
            character_info := character_data.get(operator_name)
        ):
            if (character_info.get("unicode-equivalent")) is None:
                assert (
                    character_info.get("wl-unicode") is not None
                ), f"no unicode or WMA equivalent for {operator_name}"
                continue

            affix = operator_info["affix"]
            assert affix in (
                "Infix",
                "Postfix",
                "Prefix",
            ), f"affix {affix} of {operator_name} not handled"


def test_is_builtin_constant():
    """
    Check builtin constant names are operators (keys in the operator dictionary).
    """
    builtin_constant_names = [
        name for name, info in character_data.items() if info.get("is_builtin_constant")
    ]
    for constant_name in builtin_constant_names:
        assert constant_name in operator_names
