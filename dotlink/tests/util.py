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
