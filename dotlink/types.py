# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence
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

URL: TypeAlias = str


class InvalidPlan(ValueError):
    ...


@dataclass(frozen=True)
class Plan:
    root: Path
    paths: Mapping[Path, Path] = field(default_factory=dict)
    includes: Sequence[Plan] = field(default_factory=list)


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
    source: Source
    target: Target
    copy: bool
    rsync: bool
