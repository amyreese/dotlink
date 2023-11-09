# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import atexit

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from .types import InvalidPlan, Plan, Source

from .util import run

LOG = logging.getLogger(__name__)
SUPPORTED_MAPPING_NAMES = (".dotlink", "dotlink")
COMMENT = "#"
INCLUDE = "@"
SEPARATOR = "="


def discover_mapping(root: Path) -> Path:
    for filename in SUPPORTED_MAPPING_NAMES:
        if (path := root / filename).is_file():
            LOG.debug("using mapping file %s", path)
            return path
    raise FileNotFoundError(f"no dotlink mapping found in {root}")


def generate_plan(root: Path) -> Plan:
    root = root.resolve()
    path = discover_mapping(root)
    content = path.read_text()

    paths: dict[Path, Path] = {}
    includes: list[Plan] = []

    for line in content.splitlines():
        if line.lstrip().startswith(COMMENT):
            continue

        if line.startswith(INCLUDE):
            subpath = root / line[1:]
            if subpath.is_dir():
                includes.append(generate_plan(subpath))
            elif subpath.is_file():
                raise InvalidPlan(f"{line} is a file")
            else:
                raise InvalidPlan(f"{line} not found")

        elif SEPARATOR in line:
            left, _, right = line.partition(SEPARATOR)
            paths[Path(left.strip())] = Path(right.strip())

        elif line := line.strip():
            paths[Path(line)] = Path(line)

    return Plan(
        root=root,
        paths=paths,
        includes=includes,
    )


def prepare_source(source: Source) -> Path:
    if source.path:
        return source.path

    if source.url:
        # assume this is a git repo
        tmp = TemporaryDirectory(prefix="dotlink.")
        atexit.register(tmp.cleanup)
        repo = Path(tmp.name).resolve()
        run("git", "clone", "--depth=1", source.url, repo.as_posix())
        return repo

    raise RuntimeError("unknown source value")
