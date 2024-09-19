# -*- coding: utf-8 -*-
import os

# from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest

from mathics_scanner.load import load_mathics_character_yaml

yaml_data = load_mathics_character_yaml()


# This test is slow, so do only on request!
@pytest.mark.skipif(
    not os.environ.get("MATHICS_LINT"), reason="Lint checking done only when specified"
)
def test_yaml_urls():
    for k, v in yaml_data.items():
        # This code can be used to start some point down the list
        if k < "Up":
            continue
        # for field in ("unicode-reference", "wl-reference"):
        for field in ("unicode-reference",):
            url = v.get(field)
            if url:
                try:
                    with urlopen(url) as response:
                        html = response.read()
                        assert (
                            html
                        ), f"should have been able to get HTML for {k} ({url})"
                        print(f"got {k}")
                # except* (URLError, HTTPError): # for when we have 3.11+
                except Exception:
                    assert False, f"{k} ({url}) fails"
