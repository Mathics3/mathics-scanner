from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
from mathics_scanner.characters import replace_wl_with_plain_text as wl_to_unicode
from mathics_scanner.characters import replace_unicode_with_wl as unicode_to_wl
import yaml


def check_roundtrip(yaml_data: dict):
    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            u = v["wl-unicode"]
            assert (
                unicode_to_wl(wl_to_unicode(u)) == u
            ), f"key {k} unicode {u}, {wl_to_unicode[u]}"


def test_roundtrip():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file, open(
        DEFAULT_DATA_DIR / "characters.json", "r"
    ) as json_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        check_roundtrip(yaml_data)
