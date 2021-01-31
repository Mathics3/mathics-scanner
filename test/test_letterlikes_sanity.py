from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml
import json

def check_letterlikes_sanity(yaml_data: dict, json_data: dict):
    letterlikes = json_data["letterlikes"]

    yaml_llc = [v["is-letter-like"] for c in yaml_data.values()].count(True)
    json_llc = len(letterlikes)

    assert (
        yaml_llc == json_llc
    ), f"the YAML table has {yaml_llc} letter-like characters but the JSON files lists {json_llc} letterlike characters"


def test_letterlikes_sanity():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file, open(DEFAULT_DATA_DIR / "characters.json", "r") as json_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        json_data = yaml.load(json_file)
        check_letterlikes_sanity(yaml_data, json_data)

