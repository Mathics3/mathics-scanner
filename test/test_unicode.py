# -*- coding: utf-8 -*-

from test.helper import yaml_data


def test_has_unicode():
    for k, v in yaml_data.items():
        if unicode_equivalent := v.get("unicode-equivalent", None) is not None:
            assert unicode_equivalent != v.get(
                "ascii"
            ), f"In {k} - remove add unicode equivalent"

        if amslatex := v.get("amslatex-equivalent", None) is not None:
            assert (
                amslatex.isascii()
            ), f"{k} amslatex field should be ASCII is {amslatex}"
