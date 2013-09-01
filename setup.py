from setuptools import setup

from os import path
import shutil

import dotlink

if path.isfile('README.md'):
    shutil.copyfile('README.md', 'README')

setup(name='Dotlink',
      description='Automate deployment of dotfiles to local paths or remote hosts',
      version=dotlink.VERSION,
      author='John Reese',
      author_email='john@noswap.com',
      url='https://github.com/jreese/dotlink',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Topic :: Utilities',
                   'Development Status :: 4 - Beta',
                   ],
      license='MIT License',
      install_requires=[
                        'PyYAML>=3.10',
                        ],
      requires=[
                'PyYAML (>=3.10)',
                ],
      packages=['dotlink'],
      scripts=['bin/dotlink'],
      )
