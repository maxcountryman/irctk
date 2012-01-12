'''
IrcTK
-----

A simple framework for writing IRC applications.
'''

from setuptools import setup, find_packages

setup(
    name='IrcTK',
    version='0.2.3',
    url='https://github.com/maxcountryman/irctk',
    license='BSD',
    author='Max Countryman',
    author_email='maxc@me.com',
    description='A simple framework for IRC apps',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    test_suite='test_irctk'
)

