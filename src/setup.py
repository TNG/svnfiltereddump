#!/usr/bin/env python

from setuptools import setup

setup(
    name='svnfiltereddump',
    version='1.0beta',
    description='Extracts parts from Subversion repositories',
    author='Harald Wilhelmi',
    author_email='harald.wilhelmi@tngtech.com',
    url='https://github.com/HaraldWilhelmi/svnfiltereddump',
    packages=['svnfiltereddump'],
    long_description="""\
        The svnfiltereddump tool allows to extract parts of Subversion
        repositories. It is a bit like svndumpfilter or svndumpfilter2.
        But it has less limitations and has be ability to drop drop
        old revisions.
    """,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Operators",
        "Topic :: Development",
    ],
    keywords='subversion',
    license='GPL',
    install_requires=[
        'setuptools',
        'svnfiltereddump',
    ],
    entry_points = {
        'console_scripts': [
            'svnfiltereddump = svnfiltereddump.Main:run'
        ]
    }
)
