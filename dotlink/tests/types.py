# Copyright Amethyst Reese
# Licensed under the MIT license

from pathlib import Path
from unittest import TestCase

from dotlink.types import Source, Target


class TypesTest(TestCase):
    def test_source(self) -> None:
        for value, expected in (
            ("", Source(path=Path(""))),
            (".", Source(path=Path("."))),
            ("/foo/bar", Source(path=Path("/foo/bar"))),
            ("git://github.com/a/b", Source(url="git://github.com/a/b")),
            ("https://github.com/a/b.git", Source(url="https://github.com/a/b.git")),
        ):
            with self.subTest(value):
                assert Source.parse(value) == expected

    def test_target(self) -> None:
        for value, expected in (
            ("", Target(path=Path(""))),
            (".", Target(path=Path("."))),
            ("a/b", Target(path=Path("a/b"))),
            ("/foo", Target(path=Path("/foo"))),
            ("host:", Target(path=Path(""), host="host")),
            ("host:a/b", Target(path=Path("a/b"), host="host")),
            ("host:/foo", Target(path=Path("/foo"), host="host")),
            ("user@host:", Target(path=Path(""), host="host", user="user")),
            ("user@host:a/b", Target(path=Path("a/b"), host="host", user="user")),
            ("user@host:/foo", Target(path=Path("/foo"), host="host", user="user")),
        ):
            with self.subTest(value):
                assert Target.parse(value) == expected
