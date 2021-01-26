#!/usr/bin/env python3 
# This scripts reads the data from named-characters and converts it to the 
# format used by the library internally

import json
import yaml
import re

def re_from_keys(d: dict) -> str:
    """
    Takes dictionary whose keys are all strings and returns a regex that 
    matches any of the keys
    """

    # The sorting is necessary to prevent the shorter keys from obscuring the 
    # longer ones when pattern-matchig
    return "|".join(
        sorted(map(re.escape, d.keys()), key=lambda k: (-len(k), k))
    )

def get_plain_text(char_name: str, char_data: dict, use_unicode: bool) -> str:
    """
    Takes in data about a named character and returns the appropriate
    plain text representation according to use_unicode
    """
    uni = char_data.get("unicode-equivalent")

    if uni is not None:
        if use_unicode:
            return uni

        # If all of the characters in the unicode representation are valid
        # ASCII then return the unicode representation
        elif all(ord(c) < 127 for c in uni): 
            return uni

    return f"\\[{char_name}]"

def compile_tables(data: dict) -> dict:
    """
    Compiles the general table into the tables used internally by the library
    for fast access
    """

    # Conversion from WL to the fully qualified names
    wl_to_ascii_dict = {v["wl-unicode"]: get_plain_text(k, v, False)
                        for k, v in data.items()}
    wl_to_ascii_re = re_from_keys(wl_to_ascii_dict)

    # Conversion from wl to unicode
    # We filter the dictionary after it's first created to redundant entries
    wl_to_unicode_dict = {v["wl-unicode"]: get_plain_text(k, v, True)
                          for k, v in data.items()}
    wl_to_unicode_dict = {k: v for k, v in wl_to_unicode_dict.items() 
                          if k != v}
    wl_to_unicode_re = re_from_keys(wl_to_unicode_dict)

    # Conversion from unicode to wl
    unicode_to_wl_dict = {v["unicode-equivalent"]: v["wl-unicode"]
                          for v in data.values()
                          if "unicode-equivalent" in v
                          and v["has-unicode-inverse"]}
    unicode_to_wl_re = re_from_keys(unicode_to_wl_dict)

    # Character ranges of letterlikes
    letterlikes = "".join(v["wl-unicode"] for v in data.values()
                          if v["is-letter-like"])

    # All supported named characters
    named_characters = {k: v["wl-unicode"] for k, v in data.items()}

    # ESC sequence aliases
    aliased_characters = {v["esc-alias"]: v["wl-unicode"]
                          for v in data.values() if "esc-alias" in v}

    return {
        "wl-to-ascii-dict": wl_to_ascii_dict,
        "wl-to-ascii-re": wl_to_ascii_re,
        "wl-to-unicode-dict": wl_to_unicode_dict,
        "wl-to-unicode-re": wl_to_unicode_re,
        "unicode-to-wl-dict": unicode_to_wl_dict,
        "unicode-to-wl-re": unicode_to_wl_re,
        "letterlikes": letterlikes,
        "named-characters": named_characters,
        "aliased-characters": aliased_characters,
    }

with open("mathics_scanner/data/named-characters.yml", "r") as i, open("mathics_scanner/data/characters.json", "w") as o:
    # Load the YAML data
    data = yaml.load(i, Loader=yaml.FullLoader)

    # Precompile the tables
    data = compile_tables(data)

    # Dump the proprocessed dictioanries to disk as JSON
    json.dump(data, o)

