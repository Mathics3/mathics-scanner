from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml


def check_roundtrip(yaml_data: dict):
    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            u = v["wl-unicode"]
            assert (
                unicode_to_wl(wl_to_unicode(u)) == u
            ), f"key {k} unicode {u}, {wl_to_unicode[u]}"


def test_roundtrip():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        check_roundtrip(yaml_data)
