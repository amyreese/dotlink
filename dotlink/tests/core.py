# Copyright Amethyst Reese
# Licensed under the MIT license

from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase
from unittest.mock import Mock, patch

from dotlink import core
from dotlink.types import Config, InvalidPlan


class CoreTest(TestCase):
    def setUp(self) -> None:
        td = TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.dir = Path(td.name).resolve()
        self.inner = self.dir / "inner"
        self.inner.mkdir()

        (self.dir / ".dotlink").write_text(
            dedent(
                """

                # hello world
                .gitignore = gitignore
                .vimrc

                @inner

                # zsh stuff ?
                .zshrc

                """
            )
        )
        (self.inner / "dotlink").write_text(
            dedent(
                """
                Brewfile

                .zshrc
                """
            )
        )

        for f in (
            self.dir / ".vimrc",
            self.dir / ".zshrc",
            self.inner / "Brewfile",
            self.inner / ".zshrc",
        ):
            f.write_text("\n")

    def test_discover_config(self) -> None:
        for root, expected in (
            (self.dir, self.dir / ".dotlink"),
            (self.inner, self.inner / "dotlink"),
        ):
            with self.subTest(root):
                assert core.discover_config(root) == expected

    def test_generate_config(self) -> None:
        with self.subTest("inner"):
            expected = Config(
                root=self.inner,
                paths={
                    Path("Brewfile"): Path("Brewfile"),
                    Path(".zshrc"): Path(".zshrc"),
                },
            )
            assert core.generate_config(self.inner) == expected

        with self.subTest("outer"):
            expected = Config(
                root=self.dir,
                paths={
                    Path(".gitignore"): Path("gitignore"),
                    Path(".vimrc"): Path(".vimrc"),
                    Path(".zshrc"): Path(".zshrc"),
                },
                includes=[
                    Config(
                        root=self.inner,
                        paths={
                            Path("Brewfile"): Path("Brewfile"),
                            Path(".zshrc"): Path(".zshrc"),
                        },
                    )
                ],
            )
            assert core.generate_config(self.dir) == expected

        with self.subTest("empty"):
            (self.dir / "empty").mkdir()
            with self.assertRaisesRegex(FileNotFoundError, "no dotlink mapping found"):
                core.generate_config(self.dir / "empty")

        with self.subTest("include file"):
            (self.dir / "invalid").mkdir()
            (self.dir / "invalid" / "foo").write_text("\n")
            (self.dir / "invalid" / "dotlink").write_text("@foo\n")
            with self.assertRaisesRegex(InvalidPlan, "foo is a file"):
                core.generate_config(self.dir / "invalid")

        with self.subTest("include missing"):
            (self.dir / "invalid" / "dotlink").write_text("@bar\n")
            with self.assertRaisesRegex(InvalidPlan, "bar not found"):
                core.generate_config(self.dir / "invalid")

    @patch("dotlink.core.run")
    def test_prepare_source(self, run_mock: Mock) -> None:
        pass
