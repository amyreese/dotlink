dotlink
=======

dotlink is a simple script to automate deploying an arbitrary set of "dotfiles"
from a repository to either a local path or even a remote host using ssh/scp.

dotlink does not manage the dotfiles themselves, but uses a simple text file
mapping dotfile names in the repository to their ultimate location relative to
the target path.  This allows you to have files without the dot prefix, for
instance, or avoid replicating deep directory structures to track a single file.

[![Build Status](https://travis-ci.org/jreese/dotlink.png?branch=master)](https://travis-ci.org/jreese/dotlink)


setup
-----

dotlink requires Python, either version 2.7 or versions 3.2 and newer.  No
external libraries are required.

To install dotlink system-wide or in a virtualenv:

    # pip install dotlink

Or if you want to hack on dotlink a bit, clone the repo and run:

    # python setup.py develop


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
it finds a `dotfiles` mapping file unless you specify otherwise.  The target
path is also optional, and assumed to be your local home directory.

Targets can also include local paths, or remote paths accessible via ssh by
providing a hostname as well as username if different than your current login.


todo
----

Some planned features and changes are:

- Add support for remote sources, like ssh/scp, as well as git repos or tarballs
- Generate mapping file from repository contents ?


advanced
--------

If you'd like to embed dotlink within your dotfile repository,
`dotlink/dotlink.py` is a self-contained script, specifically to allow for this
use case.  Simply copy dotfile.py into your repository; it has no external
dependencies.


legal
-----

dotlink is copyright 2013 John Reese.

dotlink is licensed under the MIT license.
See the `LICENSE` file for more details.
