#!/usr/bin/env python3

import re
import os
import sys
from setuptools import setup, find_packages

with open('README.md', 'r', encoding = 'UTF-8') as README :
    LongDescription = README.read()

SRC = os.path.abspath(os.path.dirname(__file__))
PATH = os.path.join(SRC, 'maldisc/__init__.py')

def get_version():
    with open(PATH, encoding = 'UTF-8') as f:
        for line in f:
            m = re.match("__version__ = '(.*)'", line)
            if m:
                return m.group(1)
    raise SystemExit('Could not find version string.')


if sys.version_info < (3, 7):
    sys.exit('MalDisc requires Python >= 3.7.')


setup(
    name = 'maldisc',
    version = get_version(),
    description = 'MyAnimeList now in Discord!',
    author = 'Kim',
    author_email = '2003victoryy@1utar.my',
    url = 'https://github.com/LynBean/MalDisc',
    packages = find_packages(exclude = ['tests']),
    zip_safe = False,
    python_requires = '>=3.7',
    install_requires = [
        'aiohttp',
        'asyncio',
        'discord',
        'platformdirs',
        ],
    entry_points = {
        'console_scripts': ['maldisc = maldisc.__main__: main'],
    },
    classifiers = [
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    long_description = LongDescription,
    long_description_content_type = 'text/markdown',
)