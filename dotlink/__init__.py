# Copyright 2013 John Reese
# Licensed under the MIT license

"""
Automate deployment of dotfiles to local paths or remote hosts
"""

from __future__ import absolute_import

from .dotlink import Dotlink, VERSION, main
from .__version__ import __version__
