# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import atexit
import logging
from pathlib import Path
from pprint import pformat
from tempfile import TemporaryDirectory
from typing import Generator

from .actions import Action, Copy, Plan, SSHTarball, Symlink
from .types import Config, InvalidPlan, Method, Pair, Source, Target
from .util import run

LOG = logging.getLogger(__name__)
SUPPORTED_MAPPING_NAMES = (".dotlink", "dotlink")
COMMENT = "#"
INCLUDE = "@"
SEPARATOR = "="


def discover_config(root: Path) -> Path:
    for filename in SUPPORTED_MAPPING_NAMES:
        if (path := root / filename).is_file():
            LOG.debug("discover config file %s", path)
            return path
    raise FileNotFoundError(f"no dotlink mapping found in {root}")


def generate_config(root: Path) -> Config:
    root = root.resolve()
    path = discover_config(root)
    content = path.read_text()

    paths: dict[Path, Path] = {}
    includes: list[Config] = []

    for line in content.splitlines():
        if line.lstrip().startswith(COMMENT):
            continue

        if line.startswith(INCLUDE):
            subpath = root / line[1:]
            if subpath.is_dir():
                includes.append(generate_config(subpath))
            elif subpath.is_file():
                raise InvalidPlan(f"{line} is a file")
            else:
                raise InvalidPlan(f"{line} not found")

        elif SEPARATOR in line:
            left, _, right = line.partition(SEPARATOR)
            paths[Path(left.strip())] = Path(right.strip())

        elif line := line.strip():
            paths[Path(line)] = Path(line)

    return Config(
        root=root,
        paths=paths,
        includes=includes,
    )


def prepare_source(source: Source) -> Path:
    if source.path:
        return source.path.resolve()

    if source.url:
        # assume this is a git repo
        tmp = TemporaryDirectory(prefix="dotlink.")
        atexit.register(tmp.cleanup)
        repo = Path(tmp.name).resolve()
        run("git", "clone", "--depth=1", source.url, repo.as_posix())
        return repo

    raise RuntimeError("unknown source value")


def resolve_paths(config: Config, out: Path) -> Generator[Pair, None, None]:
    out = out.resolve()

    for include in config.includes:
        yield from resolve_paths(include, out)

    for left, right in config.paths.items():
        src = config.root / right
        dest = out / left
        yield src, dest


def resolve_actions(config: Config, target: Target, method: Method) -> list[Action]:
    actions: list[Action] = []

    if target.remote:
        td = TemporaryDirectory(prefix="dotlink.")
        atexit.register(td.cleanup)
        staging = Path(td.name).resolve()
        pairs = resolve_paths(config, staging)
        method = Method.copy
    else:
        pairs = resolve_paths(config, target.path)

    if method == Method.copy:
        actions += (Copy(src, dest) for src, dest in pairs)
    elif method == Method.symlink:
        actions += (Symlink(src, dest) for src, dest in pairs)
    else:
        raise ValueError(f"unknown {method = !r}")

    if target.remote:
        actions += [SSHTarball(staging, target)]

    return actions


def dotlink(source: Source, target: Target, method: Method) -> Plan:
    LOG.debug("source = %r", source)
    LOG.debug("target = %r", target)
    LOG.debug("method = %r", method)

    root = prepare_source(source)
    config = generate_config(root)
    LOG.debug("config = %s", pformat(config, indent=2))

    plan = Plan(actions=resolve_actions(config, target, method))
    LOG.debug("plan = %s", pformat(plan, indent=2))

    return plan
