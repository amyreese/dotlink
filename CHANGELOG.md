dotlink
=======

v1.0.post0
----------

Fixed readme

```
$ git shortlog -s v1.0...v1.0.post0
     2	John Reese
```


v1.0
----

Modern release

- Built with flit with modern metadata, scripts, entrypoints
- Formatted and linted with black, µsort, µfmt, and flake8
- Changelog
- Github actions

```
$ git shortlog -s v0.6.0...v1.0
    14	John Reese
```


v0.6.0
------

Feature release:

feature: added support for deploying with rsync instead of scp
feature: --rsync flag enables use of rsync for remote deployments

```
$ git shortlog -s v0.5.0...v0.6.0
     1	John Reese
```


v0.5.0
------

Feature release:

- feature: added support for remote sources via git repositories
- feature: added --git to force using a remote git source
- change: reorganized readme to put todo after advanced usage

```
$ git shortlog -s v0.4.3...v0.5.0
     4	John Reese
```


v0.4.3
------

Bug fix release

- bugfix: relative import paths are now correctly followed from the path of
  the mapping file rather than the current working directory.

```
$ git shortlog -s v0.4.2...v0.4.3
     1	John Reese
```


v0.4.2
------

Minor version bump

- change: Added manifest for building pypi packages to include README and LICENSE

```
$ git shortlog -s v0.4.1...v0.4.2
     5	John Reese
```


v0.4.1
------

Bug fix release

- feature: added -V argument to output dotlink version and exit
- bugfix: preserve dotfile mapping order to allow dependent dotfiles to install correctly

```
$ git shortlog -s v0.4.0...v0.4.1
     5	John Reese
```


v0.4.0
------

- feature: include external dotfile mappings via `#include "filename"`
- bugfix: implied dotfile target name wasn't implemented
- text: readme cleanups
- text: clarify that "Dotlink" is now officially "dotlink"

```
$ git shortlog -s v0.3.1...v0.4.0
     4	John Reese
```


v0.3.1
------

Bug fix release

```
$ git shortlog -s v0.3.0...v0.3.1
     4	John Reese
```


v0.3.0
------

Source path is now a positional argument.

```
$ git shortlog -s v0.2.0...v0.3.0
     2	John Reese
```


v0.2.0
------

No longer depends on YAML for parsing the dotfile mapping.

```
$ git shortlog -s v0.2.0
    17	John Reese
```

