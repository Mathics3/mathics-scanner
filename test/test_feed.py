# -*- coding: utf-8 -*-

import tempfile

from mathics_scanner.feed import FileLineFeeder, MultiLineFeeder, SingleLineFeeder
from mathics_scanner.location import ContainerKind


def test_multi():
    """Test MultiLineFeeder class"""
    feeder = MultiLineFeeder("abc\ndef", "<test_multi>", ContainerKind.STRING)
    assert feeder.feed() == "abc\n", "MultiLineFeeder reads first line"
    assert feeder.feed() == "def", "reads second line"
    assert feeder.feed() == "", "Returns '' when no more lines"
    assert feeder.empty(), "MultiLineFeeder detects feeder empty condition"


def test_single():
    """Test SingleLineFeeder class"""
    feeder = SingleLineFeeder("abc\ndef", "<test_single>", ContainerKind.STRING)
    assert feeder.feed() == "abc\ndef", "SingleLineFeeder returns multiple lines"
    assert feeder.empty(), "SingleLineFeeder detects feeder empty condition"
    assert feeder.feed() == ""


def test_file():
    """Test FileLineFeeder class"""
    with tempfile.TemporaryFile("w+") as f:
        f.write("abc\ndef\n")
        f.seek(0)
        feeder = FileLineFeeder(f)
        assert feeder.feed() == "abc\n", "FileLineFeeder reads first line"
        assert feeder.feed() == "def\n", "FileLineFeeder reads second line"
        assert feeder.feed() == "", "FileLineFeeder detects feeder empty condition"
        assert feeder.empty()
