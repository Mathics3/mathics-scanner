from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml
import json

with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file:
    yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)

with open(DEFAULT_DATA_DIR / "characters.json", "r") as json_file:
    json_data = json.load(json_file)
