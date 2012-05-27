'''
IrcTK
-----

A simple framework for writing IRC applications.
'''

import irctk

import os
import sys

from setuptools import setup, find_packages

if sys.argv[-1] == 'test':
    nosetests = 'nosetests -v --with-coverage --cover-package=irctk'
    try:
        import yanc
        nosetests += ' --with-yanc'
    except ImportError:
        pass
    os.system('pyflakes irctk tests; '
              'pep8 irctk tests && '
              + nosetests)
    sys.exit()

setup(
    name='IrcTK',
    version=irctk.__version__,
    url='https://github.com/maxcountryman/irctk',
    license='BSD',
    author='Max Countryman',
    author_email='maxc@me.com',
    description='A simple framework for IRC apps',
    long_description=__doc__,
    packages=find_packages(),
    platforms='any',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    zip_safe=False,
)
