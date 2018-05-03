NAME
===
svnfiltereddump - extracts parts from Subversion repositories

SYNOPSIS
===
    svnfiltereddump [OPTIONS] SOURCE-REPO PATH ... | svnadmin load ... 
    svnfiltereddump [OPTIONS] SOURCE-REPO --include-file FILE ... | svnadmin load ...

DESCRIPTION
===
The svnfiltereddump tool is meant to extract portions of repositories of the Subversion source control system. It's output can be loaded with Subversion's `svnadmin load` command into a new Subversion repository. The source repository must be given on the command line. A list of paths to extract may given on command line or in one or more input file(s). It is also possible to skip the revision history before a given starting revision.

OPTIONS
===
**-h, --help** Shows the usage and help text and exits.

**--include-file=FILE** Read paths to include from given file. Empty lines will be ignores.

**--exclude=PATH** Exclude given path during filtering.

**--exclude-file=FILE** Read paths to exclude from given file. Empty lines will be ignores.

**--keep-empty-revs** Copy revisions even if they have no effect on included paths at all. Without this option the command operates similar to svndumpfilter with the **--drop-empty-revs** option.

**--start-rev=NUMBER** Squash the revision history below the given revision. Generate a artificial first revision with represents the given revision. If you use this option you should exclude tags and branches referring to the old revisions too. Otherwise your new repository may get huge because every tag or branch based on obsolete revisions will be included as full copy. Consider to use the **--drop-old-tags-and-branches** option.

**--no-extra-mkdirs** By default the first revision dumped will include nodes to create the parent directories of the extracted directories. Most of the time this fine. However loading such a dump into a repository, which is not empty may fail because one of the directories exists already. If that happens use this flag to disable this feature. However with is option you are responsible to create all the needed parent directories in the target repository.

**--drop-old-tags-and-branches** Use this option with the **--start-rev** option. Automatically exclude all tags and branches, which are based on a revision older than the given start revision. Please note that tagging and branching in Subversion is done by convention. So this feature is just a heuristics, which may fail in a number of ways. The directories excluded are reported and should be checked carefully.

**--tag-or-branch-dir=NAME** Use this option with **--drop-old-tags-and-branches**. By default directories called tags and branches are assumed to contain tags and branches. You may overwrite the list by giving one or more of this options. If at least one **--tag-or-branch-dir** option is given you always start with an empty list. E.g if you just run with ´**--tag-or-branch-dir=branches**´ directories called ´tags´ are no longer considered by the **--drop-old-tags-and-branches** option.

**--trunk-dir=NAME** Use this option with **--drop-old-tags-and-branches**. By default it will be assumed that directories called trunk have no tags or branches below them - even if by chance some directory below them is called 'tags' or 'branches'. If you diverted from the convention and called your trunk directories differently you can supply your name(s) with **--trunk-dir=NAME**. It works similar to the **--tag-or-branch-dir=NAME** option.

**-q, --quiet** Only report errors and warnings on console.

**-l FILE, --log-file=FILE** Write messages to given log file.

EXAMPLES
===
The most common use case is to extract some trees from an existing repository. Assume you have a repository at /repos/old. It contains two modules module/a and module/b - both with there own trunk/tags/branches structure - and you want to isolate this two modules in their own repository /repos/new. You can do this:


    svnadmin create /repos/new
    svnfiltereddump /repos/old module/a module/b | svnadmin load --ignore-uuid /repos/new

Things get a little more complicated if the two modules share one trunk/tags/branches structure with some other modules. So we first need a list of tags/branches we are actually interested in:



    last_rev=`svnlook youngest /repos/old`
    svnlook tree -r $last_rev --full-paths /repos/old | grep -E '^branches/[^/]+/module/[ab]/$' >list 
    svnlook tree -r $last_rev --full-paths /repos/old | grep -E '^tags/[^/]+/module/[ab]$' >>list 
    echo trunk/module/a >>list 
    echo trunk/module/b >>list

Now we can use this list to get our target repository as above:


	svnadmin create /repos/new 
	svnfiltereddump /repos/old --include-file list | svnadmin load --ignore-uuid /repos/new

Now lets assume we want to get rid of ancient revision history before the revision 120232. When we can do this:


	svnadmin create /repos/new 
	svnfiltereddump /repos/old --start-rev 120232 --drop-old-tags-and-branches / | svnadmin load --ignore-uuid /repos/new

It's also possible to merge two repositories. This is easy if the paths are all different. If the paths you import from two repositories have a common prefix (e.g. trunk/...) things are more interesting. Assume we want to import the path common/prefix/somewhere/a from /repos/old_a and common/prefix/elsewhere/b from /repos/old_b to /repos/new. If we do it as above the `svnadmin load` will fail because it tries to create the directory common which was already created by the first one. You may have found the option **--no-extra-mkdirs** already. However if we just give this option, for the second repository we fail again - this time because nobody created common/prefix/elsewhere. So we have to do this manually like this:


	svnadmin create /repos/new 
	svnfiltereddump /repos/old_a common/prefix/somewhere/a | svnadmin load --ignore-uuid /repos/new 
	svn mkdir -m 'merging repos' file:///repos/new/common/prefix/elsewhere 
	svnfiltereddump --no-extra-mkdirs /repos/old_b common/prefix/elsewhere/b | svnadmin load --ignore-uuid /repos/new

MANUAL INSTALLATION INSTRUCTIONS
===
Sometimes you may have to bring this tool to a machine without root permissions or Internet access. In this case follow this check list:

Prerequisite: You need a UNIX-like box.
--

Linux will work almost certainly. Other UNIX-like should work without or with minor adaption. Systems with backslashes in their path names or without IPC via pipes will never work.

Prerequisite: Python 2.X, >=2.6 must be installed.
--

In doubt run the tests.

Prerequisite: Subversion must be installed
--

The commands `svn`, `svnadmin`, and `svnlook` must be included in the default search path ($PATH). Version 1.6.x and 1.7.x are believed to work. Again in doubt run the tests. Versions 1.6.17 and 1.7.0 were tested.

**Copy the source tree to the machine.**

**Set $PYTHONPATH**

Point the environment variable PYTHONPATH to the src directory.

**Set $PATH**

Add the directory containing the svnfiltereddump command (src/bin) to the default search path.

**Install the man page**

If you want to have this man page do a gzip on it and throw it into a suitable man directory (e.g. /usr/local/man/man1 or /usr/share/man/man1) or add the directory it lies in to your MANPATH environment variable.

RUNNING THE TESTS
===
If you do anything funny run the automatic tests. To do this easily you need the nose package. One way to get nose is using pip (http://pypi.python.org/pypi/pip). To run the tests just say nosetests in the folder containing the various test folders (tests, functional_tests, integration_tests). You may pass folder or test case names to nosetests to run just some of the tests.

The tests folder contains classic unit tests which run very fast. The tests in the integration_tests folder focus of the interaction of the tool with your Subversion installation and the operating system. The tests in the functional_tests folder test the tool as a whole on a high level.

WARNINGS AND LIMITATIONS
===

Designed for Python 2.6+. The Tool was developed with Python 2.6 in mind. It hopefully works with much newer versions, but certainly not with older ones and not with Python 3.X.

Tested with Subversion 1.6.17, 1.7.0, 1.8.10, and 1.10.0. The tool was tested varies versions of Subversion. Subversion 1.8 requires version 1.1. It should work with no or minimal changes with most version of Subversion, where command `svnadmin dump` produces dump format 2 (check the first lines of the dump output). However it is very sensitive to the errors and warnings produced by Subversion commands. The respective checks may need some tweaking for some versions of Subversion. In doubt look at the code in src/svnfiltereddump/SvnRepository.py.

The option **--drop-old-tags-and-branches** uses just heuristics. Multiple ways are known to confuse the tool when using this option. It is absolutely essential to verify the list of automatically excluded directories.

There is no **--renumber-revs** option. Early versions of this tool had a option **--renumber-revs** like `svndumpfilter` and `svndumpfilter2`. The functional tests however showed that it is not of much use. Regardless how the `svnfiltereddump` renumbered the revisions - `svnadmin load` always assigned the revision numbers the same way. So this option was removed as useless.

PERFORMANCE CONSIDERATIONS
===

This tool is optimized to extract small portions from large repositories where only few revisions in the source repository are relevant for the target repository. It calls `svnadmin dump` only for the revisions which are actually relevant for the output. So it may be much faster than e.g. `svndumpfilter2` if only few revisions need to be dumped. On the other hand it may be slower than `svndumpfilter2` if almost all revisions must be dumped - especially if the revisions only contain little data.

The time complexity is expected to grow linear in the size of the revisions it has to scan and logarithmic in depth of the directory trees, which are configured to be included/excluded.

Revision data is streamed over constant size buffers - typically just 1MB. The only structure that is expected to grow tracks the mapping of input to output revisions. So memory consumption should be very moderate and grow linear with the number of input revisions processed.

REPORTING BUGS
===
Normally you will have to do the first analysis of any problem yourself (unless you are willing #1 to give other people shell access to your Subversion server over the Internet #2 to pay TNG Technology Consulting to do this work for you and #3 someone at TNG has the time to do the job). Sorry for that. First check that source repository is fine. This can be done with `svnadmin verify` command. If it is fine, go on with the path and revision you find in the error messages. Use 'svn log' and 'svn ls' to explore your source repository. Possibly use `svnadmin dump --incremental` on the offending revision. Hopefully this be will sufficient to understand what went wrong.

The preferred way to describe a bug is to write a functional test like the ones coming with the tool. If you are unable to do this, you may have to describe your problem as a sequence of svn commands to setup a minimal example repository plus your failing `svnfiltereddump` command. Please include the console output or log file produced by your run. If the problem is not obvious you may have to describe what is bad about the resulting dump.

Add your operating system, Python version, Subversion version to the above data and send it to harald.wilhelmi@tngtech.com.

HISTORY AND CREDITS
===
In 2011 the author had to reorganize a huge repository for a customer. This mostly meant splitting it in smaller parts and getting rid of old junk (someone had check-in huge amounts of static web content, which had been migrated to a CMS later). The tool `svndumpfilter2` from Simon Tatham proved highly valuable. Actually all of the new repositories but the very last one were created with this tool.

The last of the new repositories was so weired that the author hit all the limitations of `svndumpfilter2`. So he had to learn Python to remove them one by one. The result was almost a complete rewrite `svndumpfilter2`. When he was done he asked his customer for permission to publish this script - together with his thanks to Simon Tatham. However the customer denied this permission.

The author was not willing to except this outcome. So he teamed up with some people from his own company TNG Technology Consulting GmbH to write a new tool from scratch. `svnfiltereddump` started as an exercise in Python test driven development at TNG Technology Consulting in Munich, September 2011. The first release was finished by the author with some support of his colleagues in October of the same year. The initial release was create mostly the author's free time but sponsored by TNG Technology Consulting GmbH by allowing him to do some of the work during the regular training/education sessions at the company's site.

Of cause this tool is designed to outperform `svndumpfilter2` in almost every respect. However the author would like to point out that this tool would probable never have existed, if Simon Tatham had not decided to publish his tool. It was valuable source of inspiration and information.

AUTHORS
===
Written by Harald Wilhelmi with the friendly support of Thomas Fenzl and Bernd Stolle.

COPYRIGHT AND LICENSE
===
Copyright © 2011 Harald Wilhelmi 
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>. 
This is free software: you are free to change and redistribute it. 
There is NO WARRANTY, to the extent permitted by law.

SOURCE

The official address to get this tool is https://github.com/TNG/svnfiltereddump.

SEE ALSO

svn(1), svnadmin(1), http://svn.tartarus.org/sgt/svn-tools/svndumpfilter2?view=markup

This HTML page was made with roffit.
