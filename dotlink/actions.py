# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import shutil

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

from .types import Target


@dataclass
class Plan:
    actions: list[Action]

    def __str__(self) -> str:
        lines = ["Plan:"] + [str(action) for action in self.actions]
        return "\n  ".join(lines)

    def execute(self) -> Generator[Action, None, None]:
        for action in self.actions:
            action.prepare()

        for action in self.actions:
            yield action
            action.execute()


class Action:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.print()}"

    def print(self) -> str:
        return f"{self.args!r}, {self.kwargs!r}"

    def prepare(self) -> None:
        pass

    def execute(self) -> None:
        raise NotImplementedError


class Copy(Action):
    def __init__(self, src: Path, dest: Path) -> None:
        self.src = src
        self.dest = dest

    def print(self) -> str:
        return f"{self.src} -> {self.dest}"

    def prepare(self) -> None:
        if not self.src.exists():
            raise FileNotFoundError(f"{self.src} does not exist")

        if not self.dest.is_symlink() and (
            (self.dest.is_dir() and self.src.is_file())
            or (self.dest.is_file() and self.src.is_dir())
        ):
            raise RuntimeError(f"file/dir type mismatch {self.src} != {self.dest}")

        self.dest.parent.mkdir(parents=True, exist_ok=True)

    def execute(self) -> None:
        if self.src.is_dir():
            if self.dest.is_symlink():
                self.dest.unlink(missing_ok=True)
            shutil.copytree(self.src, self.dest, dirs_exist_ok=True)
        else:
            self.dest.unlink(missing_ok=True)
            shutil.copyfile(self.src, self.dest)


class Symlink(Copy):
    def prepare(self) -> None:
        if not self.dest.is_symlink() and self.dest.is_dir():
            raise RuntimeError(f"symlink destination {self.dest} is a directory")
        super().prepare()

    def execute(self) -> None:
        self.dest.unlink(missing_ok=True)
        self.dest.symlink_to(self.src)


class Deploy(Action):
    def __init__(self, src: Path, target: Target) -> None:
        self.src = src
        self.target = target

    def print(self) -> str:
        return f"{self.src} -> {self.target}"
