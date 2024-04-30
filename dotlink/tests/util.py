# Copyright Amethyst Reese
# Licensed under the MIT license

import shutil
from unittest import TestCase

from dotlink import util


class UtilTest(TestCase):
    def test_run_hello_world(self) -> None:
        python = shutil.which("python")
        assert python
        result = util.run(python, "-c", 'print("hello world")', capture_output=True)
        assert result.stdout == "hello world\n"

    def test_sha1(self) -> None:
        for value, expected in (
            ("", "da39"),
            ("hello", "aaf4"),
            ("https://github.com/amyreese/dotfiles", "01de"),
        ):
            with self.subTest(value):
                self.assertEqual(expected, util.sha1(value))
