dotlink
=======

Automate deployment of dotfiles to local paths or remote hosts

[![version](https://img.shields.io/pypi/v/dotlink.svg)](https://pypi.org/project/dotlink)
[![changelog](https://img.shields.io/badge/change-log-blue)](https://github.com/amyreese/dotlink/blob/main/CHANGELOG.md)
[![license](https://img.shields.io/pypi/l/dotlink.svg)](https://github.com/amyreese/dotlink/blob/main/LICENSE)


install
-------

    $ pipx install dotlink


usage
-----

List your dotfiles in a simple text format named either `.dotlink` or `dotlink`:

    # comments are lines starting with hash

    # simple file listing
    .vimrc
    .zshrc

    # map files to different names/paths (destination = source)
    .config/htop/htoprc = htoprc

    # include configs from submodules or other directories
    @submodule/

See example repo/config at https://github.com/amyreese/dotfiles

Tell dotlink where your dotfile repo is, and where it should put things.
Defaults to the current directory and your home directory, respectively:

    $ dotlink [<source>] [<destination>]

Use `--plan` to see what dotlink will do before doing it:

    $ dotlink --plan [...]

The source can be a cloneable git repo:

    $ dotlink https://github.com/amyreese/dotfiles.git

The destination can be a remote, ssh-able location:

    $ dotlink <source> [<user>@]host:/path/to/destination


legal
-----

dotlink is copyright [Amethyst Reese](https://noswap.com).

dotlink is licensed under the MIT license.
See the `LICENSE` file for more details.
