# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_letterlikes_sanity():
    print("test_letterlikes_sanity and letterlike need going over")
    return

    # letterlikes = json_data["letterlikes"]

    # yaml_llc = [v["is-letter-like"] for v in yaml_data.values()].count(True)
    # json_llc = len(letterlikes)

    # if yaml_llc != json_llc:
    #     yaml_letterlikes = {k:v for k,v in yaml_data.items() if v.get("is-letter-like")}
    #     y = set([v.get("unicode-equivalent", v.get("wl-unicode")) for v in yaml_data.values() if v["is-letter-like"]])
    #     j = set([c for c in letterlikes])
    #     diff = y - j
    #     diff_list = [k for k,v in yaml_letterlikes.items() if v.get("unicode-equivalent", v.get("wl-unicode")) in diff]

    #     for dl in diff_list:
    #         print(dl)
    #     diff = j - y
    #     print(diff)
    # assert (
    #     yaml_llc == json_llc
    # ), f"the YAML table has {yaml_llc} letter-like characters but the JSON files lists {json_llc} letterlike characters"
