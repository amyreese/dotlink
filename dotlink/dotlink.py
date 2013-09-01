#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

from os import path

VERSION = '0.1.1'

class Dotlink(object):
    """Copy or symlink dotfiles from a profile repository to a new location,
    either a local path or a remote path accessible via ssh/scp.

    See https://github.com/jreese/dotlink for more information."""

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description=Dotlink.__doc__)
        parser.add_argument('-d', '--debug', action='store_true', default=False,
                            help='enable debug output')
        parser.add_argument('-c', '--copy', action='store_true', default=False,
                            help='copy files rather than link')
        parser.add_argument('-m', '--map', type=str, default=None,
                            help='path to dotfile mapping YAML file')
        parser.add_argument('-s', '--source', type=str, default=None,
                            help='path to source dotfiles')

        parser.add_argument('target', type=str, nargs='?', default=None,
                            help='target path for dotfiles; either a local path'
                                 ' or a remote ssh/scp path.  Examples:'
                                 ' /home/user server:some/path'
                                 ' user@server:some/path')

        args = parser.parse_args()

        if args.target:
            match = re.match(r'(?:(?:([a-zA-Z0-9]+)@)?([^:]+):)?((?:/?[^/])*)',
                             args.target)
            if match:
                args.user, args.server, args.path = match.groups()
            else:
                parser.error('target did not pass regex')

        else:
            args.user = None
            args.server = None
            args.path = os.path.expanduser('~')

        if args.server:
            args.copy = True

        if args.map and not path.isfile(args.map):
            parser.error('map file not found')

        if args.source and not path.isdir(args.source):
            parser.error('source dir not found')

        return args

    @staticmethod
    def setup_logger(args):
        logging.addLevelName(logging.DEBUG, 'DBG')
        logging.addLevelName(logging.INFO, 'INF')
        logging.addLevelName(logging.WARNING, 'WRN')
        logging.addLevelName(logging.ERROR, 'ERR')

        log = logging.getLogger()
        log.setLevel(logging.DEBUG)

        sh = logging.StreamHandler(sys.stdout)

        if args.debug:
            fm = logging.Formatter('%(levelname)s %(message)s')
            sh.setLevel(logging.DEBUG)
        else:
            fm = logging.Formatter('%(message)s')
            sh.setLevel(logging.INFO)

        sh.setFormatter(fm)
        log.addHandler(sh)

        return log

    def sh(self, *command, **kwargs):
        self.log.debug('shell: %s', ' '.join(command))
        return subprocess.check_call(' '.join(command), stdout=sys.stdout,
                                                        stderr=sys.stderr,
                                                        stdin=sys.stdin,
                                                        shell=True, **kwargs)

    def ssh(self, *command):
        if self.args.user:
            ssh_spec = '{0}@{1}'.format(self.args.user, self.args.server)
        else:
            ssh_spec = self.args.server

        return self.sh('ssh', ssh_spec, *command)

    def scp(self, local_file, remote_path=''):
        if self.args.user:
            upload_spec = '{0}@{1}:{2}'.format(self.args.user,
                                               self.args.server,
                                               remote_path)
        else:
            upload_spec = '{0}:{1}'.format(self.args.server, remote_path)

        return self.sh('scp', local_file, upload_spec)

    def __init__(self):
        self.args = Dotlink.parse_args()
        self.log = Dotlink.setup_logger(self.args)

    def run(self):
        script = path.realpath(__file__)
        self.log.debug('Running from %s with arguments: %s', script, self.args)

        if self.args.source:
            self.source = self.args.source
        else:
            # hardcoding as the parent-parent of the script for now
            self.source = path.dirname(path.dirname(script))
        self.log.debug('Sourcing dotfiles from %s', self.source)

        try:
            self.deploy_dotfiles(self.load_dotfiles())
        except:
            self.log.exception('Profile deploy failed')

    def load_dotfiles(self):
        import yaml # do this here so that setup.py can import dotlink.VERSION

        if self.args.map and path.exists(self.args.map):
            dotfiles_path = self.args.map
        else:
            # try finding it in the source directory
            dotfiles_path = path.join(self.source, 'dotfiles.yaml')

        self.log.debug('Loading dotfile mapping from %s', dotfiles_path)

        with open(dotfiles_path) as fh:
            dotfiles = yaml.load(fh)
            self.log.debug('Found %d dotfile mappings', len(dotfiles))
            return dotfiles

    def deploy_dotfiles(self, dotfiles):
        if self.args.server:
            return self.deploy_remote(dotfiles)
        else:
            return self.deploy_local(dotfiles)

    def deploy_remote(self, dotfiles):
        try:
            tempdir_path = tempfile.mkdtemp()
            self.log.debug('Deploying to temp dir %s', tempdir_path)
            self.deploy_local(dotfiles, target_root=tempdir_path)

            fh, tempfile_path = tempfile.mkstemp(suffix='.tar.gz')
            os.close(fh)

            self.log.debug('Creating tar file %s', tempfile_path)
            shutil.make_archive(tempfile_path.replace('.tar.gz', ''),
                                'gztar', tempdir_path)

            upload_path = '_profile_upload.tgz'
            self.log.debug('Uploading tarball to %s', upload_path)
            self.scp(tempfile_path, upload_path)

            ssh_command = "'mkdir -p {0} && tar xf _profile_upload.tgz -C {0} "\
                          "&& rm -f _profile_upload.tgz'".format(self.args.path)
            self.log.debug('Using ssh to unpack tarball and clean up')
            self.ssh(ssh_command)

        finally:
            if path.isdir(tempdir_path):
                self.log.debug('Removing temp dir %s', tempdir_path)
                shutil.rmtree(tempdir_path)
            if path.isfile(tempfile_path):
                self.log.debug('Removing temp file %s', tempfile_path)
                os.unlink(tempfile_path)

    def deploy_local(self, dotfiles, target_root=None):
        if target_root == None:
            target_root = self.args.path

        for source_path, target_path in dotfiles.items():
            source_path = path.join(self.source, source_path)
            target_path = path.join(target_root, target_path)

            if path.isfile(target_path):
                self.log.debug('Removing existing file at %s', target_path)
                os.unlink(target_path)

            elif path.isdir(target_path):
                self.log.debug('Removing existing dir at %s', target_path)
                shutil.rmtree(target_path)

            parent_dir = path.dirname(target_path)
            if not path.isdir(parent_dir):
                self.log.debug('Creating parent dir %s', parent_dir)
                os.makedirs(parent_dir)

            if self.args.copy:
                if path.isdir(source_path):
                    self.log.debug('Copying file %s to %s', source_path, target_path)
                    shutil.copytree(source_path, target_path)
                else:
                    self.log.debug('Copying dir %s to %s', source_path, target_path)
                    shutil.copy(source_path, target_path)

            else:
                self.log.debug('Symlinking %s -> %s', target_path, source_path)
                os.symlink(source_path, target_path)

if __name__ == '__main__':
    Dotlink().run()
