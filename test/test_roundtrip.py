from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml
import json


def check_roundtrip(yaml_data: dict, json_data: dict):
    wl_to_unicode = json_data["wl-to-unicode-dict"]
    unicode_to_wl = json_data["unicode-to-wl-dict"]
    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            u = v["wl-unicode"]
            assert (
                unicode_to_wl[wl_to_unicode[u]] == u
            ), f"key {k} unicode {u}, {wl_to_unicode[u]}"


def test_roundtrip():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file, open(
        DEFAULT_DATA_DIR / "characters.json", "r"
    ) as json_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        json_data = json.load(json_file)
        check_roundtrip(yaml_data, json_data)
