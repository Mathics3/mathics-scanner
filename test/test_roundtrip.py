from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
from mathics_scanner.characters import replace_wl_with_plain_text as wl_to_unicode
from mathics_scanner.characters import replace_unicode_with_wl as unicode_to_wl
import yaml


def check_roundtrip(yaml_data: dict, json_data: dict):
    wl_to_unicode_dict = json_data["wl-to-unicode"]
    unicode_to_wl_dict = json_data["unicode-to-wl"]

    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            wl = v["wl-unicode"]
            assert (
                unicode_to_wl(wl_to_unicode(wl)) == wl
            ), f"key {k} unicode {uni}, {wl_to_unicode(u)}"

            uni = v["unicode-equivalent"]
            if uni != wl:
                assert (
                    uni == wl_to_unicode_dict[wl]
                ), f"key {k} unicode {uni}, {wl_to_unicode[u]}"

                assert (
                    uni in unicode_to_wl_dict
                ), f"key {k} has a non-trivial unicode inverse but isn't included in unicode-to-wl-dict"

                assert (
                    unicode_to_wl_dict[uni] == wl
                ), f"key {k} unicode {uni}, {wl_to_unicode[u]}"


def test_roundtrip():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file, open(DEFAULT_DATA_DIR / "characters.json", "r") as json_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        json_data = json.load(json_file)
        check_roundtrip(yaml_data, json_data)
