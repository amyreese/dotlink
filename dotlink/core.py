# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import atexit
import logging
from pathlib import Path
from pprint import pformat
from tempfile import TemporaryDirectory
from typing import Generator

from platformdirs import user_cache_dir

from .actions import Action, Copy, Plan, SSHTarball, Symlink
from .types import Config, InvalidPlan, Method, Pair, Source, Target
from .util import run, sha1

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
            subsource = Source.parse(line[1:], root=root)
            if subsource.path:
                try:
                    assert subsource.path.relative_to(root)
                except ValueError as e:
                    raise InvalidPlan(
                        f"non-relative include paths not allowed ({line!r} given)"
                    ) from e

            subpath = prepare_source(subsource)

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


def repo_cache_dir(source: Source) -> Path:
    assert source.url is not None
    if source.ref:
        key = f"{sha1(source.url)}-{source.stem}-{source.ref}"
    else:
        key = f"{sha1(source.url)}-{source.stem}"
    cache_dir = Path(user_cache_dir("dotlink")) / key
    return cache_dir


def prepare_source(source: Source) -> Path:
    if source.path:
        return source.path.resolve()

    if source.url:
        # assume this is a git repo
        repo_dir = repo_cache_dir(source)
        if not repo_dir.is_dir():
            repo_dir.mkdir(parents=True, exist_ok=True)
            run("git", "clone", "--depth=1", source.url, repo_dir.as_posix())

        if source.ref:
            run(
                "git",
                "-C",
                repo_dir.as_posix(),
                "fetch",
                "--force",
                "--update-head-ok",
                "--depth=1",
                "origin",
                f"{source.ref}:{source.ref}",
            )
            run(
                "git",
                "-C",
                repo_dir.as_posix(),
                "checkout",
                "--force",
                source.ref,
            )
        else:
            run(
                "git",
                "-C",
                repo_dir.as_posix(),
                "pull",
                "--ff-only",
            )

        return repo_dir

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
        td = TemporaryDirectory(prefix="dotlink-target-")
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
