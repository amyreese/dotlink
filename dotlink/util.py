# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import shlex
import subprocess
from typing import Any


def run(*cmd: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    print(f"$ {shlex.join(cmd)}")

    kwargs.setdefault("encoding", "utf-8")
    kwargs.setdefault("check", True)
    proc = subprocess.run(cmd, **kwargs)
    return proc
