# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import auto, Enum
from pathlib import Path
from typing import Mapping, Sequence, Tuple
from urllib.parse import urlparse

from typing_extensions import Self, TypeAlias

USER_HOST_REGEX = re.compile(
    r"""
    ^
    (?:(?P<user>[^@]+)@)?
    (?P<host>[^:]+):
    (?P<path>.*)
    $
    """,
    re.X,
)

Pair: TypeAlias = Tuple[Path, Path]
URL: TypeAlias = str


class InvalidPlan(ValueError):
    ...


class Method(Enum):
    symlink = auto()
    copy = auto()


@dataclass(frozen=True)
class Config:
    root: Path
    paths: Mapping[Path, Path] = field(default_factory=dict)
    includes: Sequence[Config] = field(default_factory=list)


@dataclass(frozen=True)
class Source:
    path: Path | None = None
    url: URL | None = None

    @classmethod
    def parse(cls, value: str) -> Self:
        url = urlparse(value)
        if url.scheme and url.netloc:
            return cls(url=URL(value))
        else:
            return cls(path=Path(value))


@dataclass(frozen=True)
class Target:
    path: Path
    host: str | None = None
    user: str | None = None

    @property
    def remote(self) -> bool:
        return self.host is not None

    @property
    def address(self) -> str:
        return f"{self.user}@{self.host}" if self.user else (self.host or "")

    def __str__(self) -> str:
        if self.host:
            if self.user:
                return f"{self.user}@{self.host}:{self.path}"
            else:
                return f"{self.host}:{self.path}"
        else:
            return self.path.as_posix()

    @classmethod
    def parse(cls, value: str) -> Self:
        if match := USER_HOST_REGEX.match(value):
            path = Path(match.group("path"))
            host = match.group("host")
            user = match.group("user")

            return cls(path=path, host=host, user=user)
        else:
            return cls(path=Path(value))


@dataclass(frozen=True)
class Options:
    dry_run: bool


@dataclass(frozen=True)
class Result:
    error: bool = False
