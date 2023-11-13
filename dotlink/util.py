# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import shlex
import subprocess
from typing import Any


def run(*cmd: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    print(f"$ {shlex.join(cmd)}")

    proc = subprocess.run(cmd, encoding="utf-8", check=True, **kwargs)
    return proc
