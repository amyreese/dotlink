# Copyright 2021 John Reese
# Licensed under the MIT license

"""
Automate deployment of dotfiles to local paths or remote hosts
"""

from .__version__ import __version__
from .dotlink import Dotlink, VERSION, main
