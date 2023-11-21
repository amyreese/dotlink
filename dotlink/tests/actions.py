# Copyright Amethyst Reese
# Licensed under the MIT license

import os
import platform
import tarfile
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import skipIf, TestCase
from unittest.mock import Mock, patch

from ..actions import Action, Copy, Deploy, Plan, SSHTarball, Symlink
from ..types import Target

CONTENT = "hello world\n"


class ActionsTest(TestCase):
    def test_plan(self) -> None:
        plan = Plan(
            actions=[
                Action("hello", 37),
                Copy(Path("a"), Path("b")),
                Symlink(Path("c"), Path("d")),
            ]
        )
        assert str(plan) == "\n  ".join(
            [
                "Plan:",
                r"Action: ('hello', 37), {}",
                "Copy: a -> b",
                "Symlink: c -> d",
            ]
        )

    def test_action(self) -> None:
        action = Action(1, 37, value="hello")
        assert str(action) == r"Action: (1, 37), {'value': 'hello'}"

        action.prepare()  # no-op

        with self.assertRaises(NotImplementedError):
            action.execute()

    def test_copy(self) -> None:
        with TemporaryDirectory() as td:
            tdp = Path(td).resolve()

            with self.subTest("file"):
                (src := tdp / "foo").write_text(CONTENT)
                dest = tdp / "bar"
                action = Copy(src, dest)
                assert str(action) == f"Copy: {tdp / 'foo'} -> {tdp / 'bar'}"
                assert not dest.exists()

                action.prepare()
                action.execute()
                assert dest.is_file()
                assert dest.read_text() == CONTENT

            with self.subTest("overwrite"):
                action = Copy(src, dest)
                dest.write_text("\n")  # empty

                action.prepare()
                action.execute()
                assert dest.is_file()
                assert dest.read_text() == CONTENT

            with self.subTest("directory"):
                (src := tdp / "in").mkdir(exist_ok=True)
                (src / "a").write_text(CONTENT)
                dest = tdp / "out"
                action = Copy(src, dest)
                assert src.is_dir()

                action.prepare()
                assert not dest.exists()

                action.execute()
                assert dest.is_dir()
                assert (dest / "a").is_file()
                assert (dest / "a").read_text() == CONTENT

            with self.subTest("merge directory"):
                (src := tdp / "in").mkdir(exist_ok=True)
                (src / "b").write_text(CONTENT)
                dest = tdp / "out"
                action = Copy(src, dest)
                assert src.is_dir()
                assert dest.is_dir()
                assert (dest / "a").is_file()

                action.prepare()
                assert not (dest / "b").exists()

                action.execute()
                assert dest.is_dir()
                assert (dest / "a").is_file()
                assert (dest / "a").read_text() == CONTENT
                assert (dest / "b").is_file()
                assert (dest / "b").read_text() == CONTENT

            with self.subTest("implicit mkdir"):
                src = tdp / "foo"
                new = tdp / "new"
                dest = new / "file"
                action = Copy(src, dest)
                assert not new.exists()
                assert not dest.exists()

                action.prepare()
                assert new.is_dir()
                assert not dest.exists()

                action.execute()
                assert dest.is_file()
                assert dest.read_text() == CONTENT

            with self.subTest("missing source"):
                src = tdp / "missing"
                action = Copy(src, dest)
                assert not src.exists()

                with self.assertRaisesRegex(
                    FileNotFoundError, "missing does not exist"
                ):
                    action.prepare()

            with self.subTest("dir -> file mismatch"):
                src = tdp / "in"
                dest = tdp / "bar"
                dest.write_text(CONTENT)
                action = Copy(src, dest)
                assert src.is_dir()
                assert dest.is_file()

                with self.assertRaisesRegex(RuntimeError, "file/dir type mismatch"):
                    action.prepare()

            with self.subTest("file -> dir mismatch"):
                src = tdp / "foo"
                src.write_text(CONTENT)
                (dest := tdp / "out").mkdir(exist_ok=True)
                action = Copy(src, dest)
                assert src.is_file()
                assert dest.is_dir()

                with self.assertRaisesRegex(RuntimeError, "file/dir type mismatch"):
                    action.prepare()

    @skipIf(platform.system() == "Windows", "symlinks unsupported on windows")
    def test_symlink(self) -> None:
        with TemporaryDirectory() as td:
            tdp = Path(td).resolve()

            with self.subTest("basic"):
                (src := tdp / "foo").write_text(CONTENT)
                dest = tdp / "bar"
                action = Symlink(src, dest)
                assert str(action) == f"Symlink: {tdp / 'foo'} -> {tdp / 'bar'}"
                assert not dest.exists()

                action.prepare()
                action.execute()
                assert dest.is_symlink()
                assert Path(os.readlink(dest)) == src
                assert dest.is_file()
                assert dest.read_text() == CONTENT

            with self.subTest("overwrite"):
                (dest := tdp / "file").write_text("\n")
                action = Symlink(src, dest)
                assert dest.is_file()

                action.prepare()
                assert not dest.is_symlink()
                assert dest.read_text() == "\n"

                action.execute()
                assert dest.is_symlink()
                assert Path(os.readlink(dest)) == src
                assert dest.read_text() == CONTENT

            with self.subTest("implicit mkdir"):
                new = tdp / "new"
                dest = new / "file"
                action = Symlink(src, dest)
                assert not new.exists()
                assert not dest.exists()

                action.prepare()
                assert new.is_dir()
                assert not dest.exists()

                action.execute()
                assert dest.is_symlink()
                assert Path(os.readlink(dest)) == src
                assert dest.is_file()
                assert dest.read_text() == CONTENT

            with self.subTest("missing source"):
                src = tdp / "missing"
                action = Symlink(src, dest)
                assert not src.exists()

                with self.assertRaisesRegex(
                    FileNotFoundError, "missing does not exist"
                ):
                    action.prepare()

            with self.subTest("abort directory"):
                src = tdp / "foo"
                dest = tdp / "new"
                action = Symlink(src, dest)
                assert src.is_file()
                assert dest.is_dir()

                with self.assertRaisesRegex(
                    RuntimeError, "symlink destination .+ is a directory"
                ):
                    action.prepare()

    def test_deploy(self) -> None:
        assert Deploy is Deploy  # TODO

    @patch("dotlink.actions.run")
    def test_sshtarball(self, run_mock: Mock) -> None:
        with TemporaryDirectory() as td:
            tdp = Path(td).resolve()

            with self.subTest("host"):
                (tdp / "one").write_text(CONTENT)
                (tdp / "foo").mkdir()
                (tdp / "foo" / "bar").write_text(CONTENT)

                action = SSHTarball(tdp, Target(Path("/target"), host="localhost"))
                action.prepare()
                action.execute()

                run_mock.assert_called_once_with(
                    "ssh",
                    "localhost",
                    "tar",
                    "-xz",
                    "-f-",
                    "-C",
                    "/target",
                    input=action.data,
                    encoding=None,
                )
                run_mock.reset_mock()

                stream = BytesIO(action.data)
                with tarfile.open("r|gz", fileobj=stream) as tf:
                    assert tf.getnames() == [
                        ".",
                        "./foo",
                        "./foo/bar",
                        "./one",
                    ]

            with self.subTest("user@host"):
                action = SSHTarball(
                    tdp, Target(Path("/target"), host="localhost", user="nobody")
                )
                action.prepare()
                action.execute()

                run_mock.assert_called_once_with(
                    "ssh",
                    "nobody@localhost",
                    "tar",
                    "-xz",
                    "-f-",
                    "-C",
                    "/target",
                    input=action.data,
                    encoding=None,
                )
                run_mock.reset_mock()

            with self.subTest("file"):
                (afile := tdp / "afile").write_text("\n")
                action = SSHTarball(afile, Target(Path("/foo"), host="localhost"))
                with self.assertRaisesRegex(RuntimeError, "afile is not a directory"):
                    action.prepare()

            with self.subTest("local target"):
                action = SSHTarball(tdp, Target(Path("/foo")))
                with self.assertRaisesRegex(ValueError, "target /foo is not remote"):
                    action.prepare()
