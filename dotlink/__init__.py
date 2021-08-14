# Copyright 2013 John Reese
# Licensed under the MIT license

"""
Automate deployment of dotfiles to local paths or remote hosts
"""

from __future__ import absolute_import

from .__version__ import __version__
from .dotlink import Dotlink, VERSION, main
