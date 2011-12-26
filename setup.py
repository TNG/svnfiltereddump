#!/usr/bin/env python

from distutils.core import setup

setup(
    name='svnfiltereddump',
    version='1.0beta4',
    description='Extracts parts from Subversion repositories',
    author='Harald Wilhelmi',
    author_email='harald.wilhelmi@tngtech.com',
    url='https://github.com/tng/svnfiltereddump',
    packages=['svnfiltereddump'],
    package_dir = { '': 'src' },
    long_description="""\
        The svnfiltereddump tool allows to extract parts of Subversion
        repositories. It is a bit like svndumpfilter or svndumpfilter2.
        But it has less limitations and has the ability to drop drop
        old revisions.
    """,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
    ],
    keywords='subversion',
    license='GPL',
    scripts = [ 'src/bin/svnfiltereddump' ]
)
