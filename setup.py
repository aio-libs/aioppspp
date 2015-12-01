# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import importlib
import os
import sys
from os.path import join
from setuptools import setup, find_packages

name = 'aioppspp'

if sys.version_info < (3, 5, 0):
    raise RuntimeError('{} requires Python 3.5.0+'.format(name))

setup_dir = os.path.dirname(__file__)
mod = importlib.import_module('{}.version'.format(name))
long_description = open(join(setup_dir, 'README.rst')).read().strip()

setup(
    name=name,
    version=mod.__version__,
    license='Apache 2',
    url='https://github.com/aio-libs/aioppspp',

    description='Implementation of the RFC-7574 PPSPP in Python/asyncio',
    long_description=long_description,

    author='Alexander Shorin',
    author_email='kxepal@gmail.com',

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],

    packages=find_packages(),
    zip_safe=False,
    test_suite='{}.tests'.format(name),

    install_requires=[

    ],
    extras_require={
        'dev': [
            'coverage==4.0.3',
            'flake8==2.5.0',
        ],
        'docs': [
            'sphinx==1.3.1',
        ]
    },
    tests_require=[
        'hypothesis==1.15.0',
    ],
)
