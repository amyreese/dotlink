dotlink
=======

dotlink is a simple script to automate deploying an arbitrary set of "dotfiles"
from a repository to either a local path or even a remote host using ssh/scp.

dotlink does not manage the dotfiles themselves, but uses a simple text file
mapping dotfile names in the repository to their ultimate location relative to
the target path.  This allows you to have files without the dot prefix, for
instance, or avoid replicating deep directory structures to track a single file.

[![version](https://img.shields.io/pypi/v/dotlink.svg)](https://pypi.org/project/dotlink)
[![changelog](https://img.shields.io/badge/change-log-blue)](https://github.com/amyreese/dotlink/blob/main/CHANGELOG.md)
[![license](https://img.shields.io/pypi/l/dotlink.svg)](https://github.com/amyreese/dotlink/blob/main/LICENSE)


install
-----

    $ pip install dotlink


usage
-----

You'll first need to create a mapping file in the root of your dotfile
repository named `.dotfiles` (or just `dotfiles`), following this format:

- Each line contains the local repository filename, optionally followed by
  a colon and the target filename if different than the local filename.
- External dotfile mappings can be included using `#include "path/to/mapping"`,
  and the requested map will be loaded as well.  The requested path can either
  be an explicit filename, or a directory containing a mapping named `dotfiles`
  or `.dotfiles`.
- Comments are denoted by lines beginning with the `#` symbol, and are ignored.

An example mapping might look like:

    # the dotfiles to care about
    aliases: .alias
    .bashrc
    .profile: .profile
    htop: .config/htop/htoprc
    vim: .vim
    vimrc: .vimrc

    # some external dotfile paths to include
    #include "repo2/dotfiles"
    #include "/full/patt/to/repo3/"

Once the mapping is in place, run dotlink, and tell it where your source
repository is, as well as where you want it to deploy to:

    $ dotlink [path/to/repository] [[[user@]host:]path/to/target]

The source path is optional; dotlink will assume it's your current directory if
it finds a `.dotfiles` mapping file unless you specify otherwise.  The target
path is also optional, and assumed to be your local home directory.

Sources can include local paths or remote git repository URLs.
Targets can also include local paths, or remote paths accessible via ssh by
providing a hostname as well as username if different than your current login.


advanced
--------

### remote sources

Sources can also point at remote locations, such as git repositories, and
dotlink will clone the remote data into a temporary path and then copy the
contents into the appropriate paths.  dotlink will guess this if your source
path begins with "git://" or "git@", but you can also use `--git` to force this
for non-standard URLs.  The following command will clone my public dotfile repo,
and install it to your home directory:

    $ dotlink git://github.com/amyreese/dotfiles

This is essentially equivalent to the following sequence of commands:

    $ git clone git://github.com/amyreese/dotfiles
    $ dotlink dotfiles
    $ rm -rf dotfiles

You can even combine remote sources with remote targets, to clone the dotfile
repository locally, and then copy the dotfiles to the remote host via scp:

    $ dotlink git://github.com/amyreese/dotfiles amyreese@devserver:


legal
-----

dotlink is copyright [Amethyst Reese](https://noswap.com).

dotlink is licensed under the MIT license.
See the `LICENSE` file for more details.
