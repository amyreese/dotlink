# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import logging
import sys

import click
from rich import print

from .__version__ import __version__
from .core import generate_plan, prepare_source
from .types import Options, Source, Target

LOG = logging.getLogger(__name__)


@click.command("dotlink")
@click.version_option(__version__, "--version", "-V")
@click.option("--debug", "-D", is_flag=True, help="enable debug output")
@click.option(
    "--copy / --symlink",
    help="choose to copy or symlink files for local targets (default: symlink)",
)
@click.option(
    "--rsync / --scp",
    help="choose to rsync or scp files for remote targets (default: scp)",
)
@click.argument("source", required=False, default=".")
@click.argument("target")
def main(
    debug: bool,
    copy: bool,
    rsync: bool,
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

    options = Options(
        source=Source.parse(source),
        target=Target.parse(target),
        copy=copy,
        rsync=rsync,
    )
    LOG.debug("%r", options)

    root = prepare_source(options.source)
    plan = generate_plan(root)
    print(plan)
