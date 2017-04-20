
svnfiltereddump
===============

The `svnfiltereddump` tool is meant to extract portions of repositories of the
Subversion source control system. It's output can be loaded with Subversion's
"svnadmin load" command into a new Subversion repository. The source
repository must be given on the command line. A list of paths to extract
may given on command line or in one or more input file(s). It is also possible
to skip the revision history before a given starting revision.

COMPATIBILITY
-------------

This tool was designed to run on Linux. It is assumed to work on other Unix-ish
systems. It will certainly not work on systems with no IPC over pipes or with
backslashes in path names.

INSTALLATION
------------

Presently the preferred way of installation is via pip:

    sudo pip install svnfiltereddump
 
MANUAL INSTALLATION
-------------------

Please look at the `svnfiltereddump` documentation.

**Online Docs**

See [svnfiltereddump.1.md](doc/svnfiltereddump.1.md) or https://cdn.rawgit.com/derFunk/svnfiltereddump/master/doc/svnfiltereddump.1.html

**Man Pages**

If it is not installed on your system, you can display it by typing

    man man/man1/svnfiltereddump.1

or

    nroff -man man/man1/svnfiltereddump.1 | less

in directory containing this README.

CHANGE HISTORY
--------------

1.2:

- Just fixed version number - no functional change to version 1.1.

1.1:

- Updated to work with Subversion 1.8.

1.0:

- Bug fix: GitHub #1 - Crash on missing Text-content-md5
  `svnfiltereddump` will no longer crash if "svnadmin dump" will write
  out a node with Text-Content and no MD5 checksum. This was observed
  with Subversion 1.7.5 and empty files.
- Bug fix: GitHub #2 - Dump fails on mergeinfo warning 0x0001
  `svnfiltereddump` will no longer crash when "svnadmin dump" writes out
  warnings like "WARNING 0x0001: Mergeinfo referencing revision(s) prior
  to the oldest dumped revision (rXXX). Loading this dump may result in
  invalid mergeinfo.".

1.0beta4:

- Bug fix: Node-action 'replace' not supported.
