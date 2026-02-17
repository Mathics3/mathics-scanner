# -*- coding: utf-8 -*-

import json

import yaml

from mathics_scanner.generate.named_characters import DEFAULT_DATA_DIR


def load_mathics3_named_characters_yaml():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return yaml_data


def load_mathics3_named_characters_json():
    with open(DEFAULT_DATA_DIR / "named-characters.json", "r") as json_file:
        json_data = json.load(json_file)
    return json_data
