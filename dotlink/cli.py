# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import logging
import sys

import click

from .__version__ import __version__
from .core import dotlink
from .types import Method, Options, Source, Target

LOG = logging.getLogger(__name__)


@click.command("dotlink")
@click.version_option(__version__, "--version", "-V")
@click.option("--debug", "-D", is_flag=True, help="enable debug output")
@click.option(
    "--dry-run",
    "--plan",
    is_flag=True,
    help="print planned actions without executing",
)
@click.option(
    "--symlink / --copy",
    default=True,
    help="use symlinks or copies (default symlink)",
)
@click.argument("source", required=False, default=".")
@click.argument("target")
def main(
    debug: bool,
    dry_run: bool,
    symlink: bool,
    source: str,
    target: str,
) -> None:
    """
    Copy or symlink dotfiles from a profile repository to a new location,
    either a local path or a remote path accessible via ssh/scp.

    Source must be a local path, or git:// or https:// git repo URL.
    Defaults to current working directory.

    Target must be a local path or remote SSH/SCP destination [[user@]host:path].

    See https://github.com/amyreese/dotlink for more information.
    """
    logging.basicConfig(
        level=(logging.DEBUG if debug else logging.WARNING),
        stream=sys.stderr,
    )

    plan = dotlink(
        source=Source.parse(source),
        target=Target.parse(target),
        method=Method.symlink if symlink else Method.copy,
    )

    if dry_run:
        print(plan)
    else:
        for action in plan.execute():
            print(action)
