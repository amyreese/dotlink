# Copyright Amethyst Reese
# Licensed under the MIT license

# flake8: noqa
# type: ignore

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from os import path
from urllib.parse import urlparse

import click

from .__version__ import __version__ as VERSION


class Dotlink:
    def parse_mapping(self, map_path, source=None, dotfiles=None):
        """Do a simple parse of the dotfile mapping, using semicolons to
        separate source file name from the target file paths."""
        include_re = r"""^\s*#include\s+(".+"|'.+')"""
        include_re = re.compile(include_re, re.I)
        mapping_re = r"""^("[^"]+"|\'[^\']+\'|[^\'":]+)\s*(?::\s*(.*)\s*)?$"""
        mapping_re = re.compile(mapping_re)

        filename = None
        map_path = path.realpath(path.expanduser(map_path))

        if path.isfile(map_path):
            filename = map_path

        elif path.isdir(map_path):
            # try finding a mapping in the target directory
            for map_name in ".dotfiles", "dotfiles":
                candidate = path.join(map_path, map_name)
                if path.isfile(candidate):
                    filename = candidate
                    break

        if filename is None:
            raise ValueError("No dotfile mapping found in %s" % map_path)

        if source is None:
            source = path.dirname(map_path)

        if dotfiles is None:
            dotfiles = OrderedDict()

        lineno = 0

        with open(filename) as fh:
            for line in fh:
                lineno += 1
                content = line.strip()

                match = include_re.match(content)
                if match:
                    include_path = match.group(1).strip("'\"")
                    if include_path.startswith("/") or include_path.startswith("~"):
                        include_path = path.realpath(path.expanduser(include_path))
                    else:
                        include_path = path.join(path.dirname(filename), include_path)

                    if path.exists(include_path):
                        self.log.debug(
                            "Recursively parsing mapping in %s", include_path
                        )
                        dotfiles = self.parse_mapping(include_path, dotfiles=dotfiles)
                    else:
                        self.log.warning(
                            "Include command points to file or "
                            'directory that does not exist, "%s",'
                            " on line %d",
                            include_path,
                            lineno,
                        )

                if not content or content.startswith("#"):
                    # comment line or empty line
                    continue

                match = mapping_re.match(content)
                if match:
                    source_path, target_path = match.groups()
                    source_path = path.join(source, source_path.strip("'\""))

                    if source_path in dotfiles:
                        self.log.warning(
                            'Duplicate dotfile source "%s" ' "on line #%d", lineno
                        )
                        continue

                    if target_path is None:
                        target_path = source_path

                    dotfiles[source_path] = target_path

                else:
                    self.log.warning(
                        "Dotfile mapping regex failed on line " "#%d", lineno
                    )

        return dotfiles

    def sh(self, *command, **kwargs):
        """Run a shell command with the given arguments."""
        self.log.debug("shell: %s", " ".join(command))
        return subprocess.check_call(
            " ".join(command),
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=sys.stdin,
            shell=True,
            **kwargs,
        )

    def ssh(self, *command):
        """Run an ssh command using the configured user/server values."""
        if self.args.user:
            ssh_spec = "{0}@{1}".format(self.args.user, self.args.server)
        else:
            ssh_spec = self.args.server

        return self.sh("ssh", ssh_spec, *command)

    def scp(self, local_file, remote_path=""):
        """Copy a local file to the given remote path."""
        if self.args.user:
            upload_spec = "{0}@{1}:{2}".format(
                self.args.user, self.args.server, remote_path
            )
        else:
            upload_spec = "{0}:{1}".format(self.args.server, remote_path)

        return self.sh("scp", local_file, upload_spec)

    def __init__(self):
        self.args = Dotlink.parse_args()
        self.log = logging.getLogger(__name__)

    def run(self):
        """Start the dotfile deployment process."""
        script = path.realpath(__file__)
        self.log.debug("Running from %s with arguments: %s", script, self.args)

        if self.args.source:
            self.source = self.args.source
        else:
            # hardcoding as the parent-parent of the script for now
            self.source = path.dirname(path.dirname(script))
        self.log.debug("Sourcing dotfiles from %s", self.source)

        try:
            if self.args.repo:
                self.clone_repo()

            self.deploy_dotfiles(self.load_dotfiles())

        except Exception:
            self.log.exception("Profile deploy failed")

        finally:
            if self.args.repo:
                self.cleanup_repo()

    def load_dotfiles(self):
        """Read in the dotfile mapping as a dictionary."""
        if self.args.map and path.exists(self.args.map):
            dotfiles_path = self.args.map
        else:
            dotfiles_path = self.source

        self.log.debug("Loading dotfile mapping from %s", dotfiles_path)

        return self.parse_mapping(dotfiles_path, source=self.source)

    def clone_repo(self):
        """Clone a repository containing the dotfiles source."""
        tempdir_path = tempfile.mkdtemp()

        if self.args.git:
            self.log.debug(
                "Cloning git source repository from %s to %s", self.source, tempdir_path
            )
            self.sh("git clone", self.source, tempdir_path)

        else:
            raise NotImplementedError("Unknown repo type")

        self.source = tempdir_path

    def cleanup_repo(self):
        """Cleanup the temporary directory containing the dotfiles repo."""
        if self.source and path.isdir(self.source):
            self.log.debug("Cleaning up source repo from %s", self.source)
            shutil.rmtree(self.source)

    def deploy_dotfiles(self, dotfiles):
        """Deploy dotfiles using the appropriate method."""
        if self.args.server:
            return self.deploy_remote(dotfiles)
        else:
            return self.deploy_local(dotfiles)

    def deploy_remote(self, dotfiles):
        """Deploy dotfiles to a remote server."""
        tempfile_path = None
        tempdir_path = None

        try:
            tempdir_path = tempfile.mkdtemp()
            self.log.debug("Deploying to temp dir %s", tempdir_path)
            self.deploy_local(dotfiles, target_root=tempdir_path)

            if self.args.rsync:
                local_spec = tempdir_path.rstrip("/") + "/"
                remote_spec = self.args.path.rstrip("/") + "/"

                if self.args.user:
                    remote_spec = "{0}@{1}:{2}".format(
                        self.args.user, self.args.server, remote_spec
                    )
                else:
                    remote_spec = "{0}:{1}".format(self.args.server, remote_spec)

                self.log.debug("Using rsync to sync dotfiles to %s", remote_spec)
                self.sh("rsync", "-az", local_spec, remote_spec)

            else:
                fh, tempfile_path = tempfile.mkstemp(suffix=".tar.gz")
                os.close(fh)

                self.log.debug("Creating tar file %s", tempfile_path)
                shutil.make_archive(
                    tempfile_path.replace(".tar.gz", ""), "gztar", tempdir_path
                )

                upload_path = "_profile_upload.tgz"
                self.log.debug("Uploading tarball to %s", upload_path)
                self.scp(tempfile_path, upload_path)

                if self.args.path:
                    ssh_command = (
                        "'mkdir -p {0} && "
                        "tar xf _profile_upload.tgz -C {0}; "
                        "rm -f _profile_upload.tgz'"
                        "".format(self.args.path)
                    )
                else:
                    ssh_command = (
                        "tar xf _profile_upload.tgz; " "rm -f _profile_upload.tgz"
                    )
                self.log.debug("Using ssh to unpack tarball and clean up")
                self.ssh(ssh_command)

        finally:
            if tempdir_path and path.isdir(tempdir_path):
                self.log.debug("Removing temp dir %s", tempdir_path)
                shutil.rmtree(tempdir_path)
            if tempfile_path and path.isfile(tempfile_path):
                self.log.debug("Removing temp file %s", tempfile_path)
                os.unlink(tempfile_path)

    def deploy_local(self, dotfiles, target_root=None):
        """Deploy dotfiles to a local path."""
        if target_root is None:
            target_root = self.args.path

        for source_path, target_path in dotfiles.items():
            source_path = path.join(self.source, source_path)
            target_path = path.join(target_root, target_path)

            if path.isfile(target_path) or path.islink(target_path):
                self.log.debug("Removing existing file at %s", target_path)
                os.unlink(target_path)

            elif path.isdir(target_path):
                self.log.debug("Removing existing dir at %s", target_path)
                shutil.rmtree(target_path)

            parent_dir = path.dirname(target_path)
            if not path.isdir(parent_dir):
                self.log.debug("Creating parent dir %s", parent_dir)
                os.makedirs(parent_dir)

            if self.args.copy:
                if path.isdir(source_path):
                    self.log.debug("Copying file %s to %s", source_path, target_path)
                    shutil.copytree(source_path, target_path)
                else:
                    self.log.debug("Copying dir %s to %s", source_path, target_path)
                    shutil.copy(source_path, target_path)

            else:
                self.log.debug("Symlinking %s -> %s", target_path, source_path)
                os.symlink(source_path, target_path)
