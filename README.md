dotlink
=======

Dotlink is a simple script to automate deploying an arbitrary set of "dotfiles"
from a repository to either a local path or even a remote host using ssh/scp.

Dotlink does not manage the dotfiles themselves, but uses a simple YAML file
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
repository name "dotfiles.yaml", containing a root-level dictionary where keys
are the file name in the repository, and the values are the path and filename
relative to your home directory that the files will be installed to.

An example mapping might look like:

    # dotfiles.yaml
    aliases: .alias
    bashrc: .bashrc
    profile: .profile
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


advanced
--------

If you'd like to embed Dotlink within your dotfile repository,
`dotfile/dotfile.py` is a self-contained script, specifically to allow for this
use case.  Simply copy dotfile.py into your repository; its only external
dependency beyond core Python is the PyYAML library.


legal
-----

Dotlink is copyright 2013 John Reese.  It is licensed under the MIT license.
See the `LICENSE` file for more details.
