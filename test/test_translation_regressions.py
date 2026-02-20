# -*- coding: utf-8 -*-

from mathics_scanner.characters import NAMED_CHARACTERS, replace_wl_with_plain_text


def check_translation_regression(c: str, expected_translation: str):
    translation = replace_wl_with_plain_text(NAMED_CHARACTERS[c])
    assert (
        translation == expected_translation
    ), f"REGRESSION {c} is translated to {translation} but it should translate to {expected_translation}"


def test_translation_regressions():
    check_translation_regression("DifferentialD", "\U0001d451")
    check_translation_regression("PartialD", "\u2202")
    check_translation_regression("Uranus", "\u2645")
    check_translation_regression("WeierstrassP", "\u2118")
