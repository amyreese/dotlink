dotlink
=======

Dotlink is a simple script to automate deploying an arbitrary set of "dotfiles"
from a repository to either a local path or even a remote host using ssh/scp.

Dotlink does not manage the dotfiles themselves, but uses a simple text file
mapping dotfile names in the repository to their ultimate location relative to
the target path.  This allows you to have files without the dot prefix, for
instance, or avoid replicating deep directory structures to track a single file.


setup
-----

To install Dotlink system-wide:

    # pip install dotlink

Or if you want to hack on Dotlink a bit, clone the repo and run:

    # python setup.py develop


usage
-----

You'll first need to create a mapping file in the root of your dotfile
repository named "dotfiles", following this format:

- Each line contains the local repository filename, optionally followed by
  a colon and the target filename if different than the local filename.
- Comments are denoted by lines beginning with the `#` symbol, and are ignored.

An example mapping might look like:

    # dotfiles
    aliases: .alias
    .bashrc
    .profile: .profile
    htop: .config/htop/htoprc
    vim: .vim
    vimrc: .vimrc

Once the mapping is in place, run Dotlink, and tell it where you repository is,
as well as where you want it to deploy to:

    $ dotlink -s path/to/repository [[[user@]host:]path/to/target]

Targets can include local paths, or remote paths accessible via ssh by
providing a hostname as well as username if different than your current login.
If you don't give a target path, Dotlink will assume you want to deploy to your
home directory; this works for remote targets too.


todo
----

Some planned features and changes are:

- Rework --source as positional parameter that defaults to $CWD
- Add support for remote sources, like ssh/scp, but also git repos or tarballs
- Generate mapping file from repository contents ?


advanced
--------

If you'd like to embed Dotlink within your dotfile repository,
`dotlink/dotlink.py` is a self-contained script, specifically to allow for this
use case.  Simply copy dotfile.py into your repository; it has no external
dependencies.


legal
-----

Dotlink is copyright 2013 John Reese.

Dotlink is licensed under the MIT license.
See the `LICENSE` file for more details.
