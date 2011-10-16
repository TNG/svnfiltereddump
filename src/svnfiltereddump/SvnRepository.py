
from os import waitpid
from string import join
from subprocess import Popen, check_call, PIPE, STDOUT
from hashlib import md5
from logging import info
import re

from ContentTin import ContentTin
from CheckedCommandFileHandle import CheckedCommandFileHandle


class RevisionInfo(object):
    def __init__(self, author, date, log_message):
        self.author = author
        self.date = date
        self.log_message = log_message

class TreeHandle(object):
    def __init__(self, file_handle, command):
        self.file_handle = file_handle
        self.command = command
    def __iter__(self):
        return self
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, trace):
        self.file_handle = None
        return False
    def next(self):
        line = self.file_handle.readline()
        if not line:
            raise StopIteration()
        if line[-1:] != "\n":
            raise Exception(
                "Line read from '%s' ('%s') has no newline. Truncated?"
                % ( self.command, line )
            )
        return line[:-1]


class SvnRepository(object):

    chunk_size = 1024**2

    def __init__(self, path):
        if path[0] != '/':
            raise Exception("Please supply abosulte path to repository!")
        self.path = path
        self.url = 'file://' + path

    def get_changed_paths_by_change_type_for_revision(self, rev):
        changes = { }
        with CheckedCommandFileHandle([ 'svnlook', 'changed', '-r', str(rev), self.path ]) as fh:
            for line in fh:
                change_type = line[:3].strip()
                path = line[4:-1]
                if line[-1:] != "\n":
                    raise Exception(
                        "Line read from 'svnlook changed -r %d %s' has no newline. Truncated?"
                        % ( rev, self.path )
                    )
                if changes.has_key(change_type):
                    changes[change_type].append(path)
                else:
                    changes[change_type] = [ path ]

        return changes

    def get_tin_for_file(self, path, rev):
        # It is ugly to read the file twice. But f we don't want to keep the whole file in
        # memory. And:  We just need to calculate the MD5 checksum BEFORE we copy it to the output.
        md5_calculator = md5()
        size = 0
        with CheckedCommandFileHandle([ 'svnlook', 'cat', '-r', str(rev), self.path, path]) as fh:
            while True:
                chunk = fh.read(self.chunk_size)
                if chunk == '':
                    break
                md5_calculator.update(chunk)
                size += len(chunk)
        md5sum = md5_calculator.hexdigest()
        fh = CheckedCommandFileHandle([ 'svnlook', 'cat', '-r', str(rev), self.path, path])
        return ContentTin(fh, size, md5sum)

    def get_properties_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        property_list = [ ]
        rev_string = str(rev)
        with CheckedCommandFileHandle([ 'svnlook', 'pl', '-r', rev_string, self.path, path]) as fh:
            for line in fh:
                if line[-1:] != "\n":
                    raise Exception(
                        "Line read from 'svnlook pl -r %d %s %s' has no newline. Truncated?"
                        % ( rev, self.path, path )
                    )
                property_list.append(line[2:-1])

        properties = { }
        for property_name in property_list:
            with CheckedCommandFileHandle([ 'svnlook', 'pg', '-r', rev_string, self.path, property_name, path]) as fh:
                property_value = fh.read()
            properties[property_name] = property_value

        return properties

    def get_type_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        args = [ 'svnlook', 'tree', '--full-paths', '-r', str(rev), self.path, path ]
        process = Popen(args, stdout=PIPE, stderr=PIPE)
        output = process.stdout.read()
        error = process.stderr.read()
        process.stdout.close()
        process.stderr.close()
        status = waitpid(process.pid, 0)[1]
        if status:
            if re.match('svnlook: (?:.*)File not found:', error):
                return None
            else:
                 raise Exception(
                    "Command '%s' exited unexpected with status %d and error message:\n%s"
                    % ( join(args), status, error )
                )
        if output.startswith(path + "/\n"):
            return 'dir'
        else:
            return 'file'

    def get_dump_file_handle_for_revision(self, rev):
        return CheckedCommandFileHandle(
            [ 'svnadmin', 'dump', '--incremental', '-r', str(rev), self.path ],
            [   # SVN 1.6
                '^\* Dumped revision \d+\.$',
                '^WARNING: Referencing data in revision \d+, which is older than the oldest$',
                '^WARNING: dumped revision \(\d+\)\.  Loading this dump into an empty repository$',
                '^WARNING: will fail\.$',
                # SVN 1.7
                'WARNING 0x0000: Referencing data in revision \d+, which is older than the oldest dumped revision \(r\d+\)',
                'WARNING 0x0000: The range of revisions dumped contained references to copy sources outside that range\.',
            ]
        )

    def get_tree_handle_for_path(self, path, rev):
        args = [ 'svnlook', 'tree', '--full-paths', '-r', str(rev), self.path, path]
        list = [ ]
        fh = CheckedCommandFileHandle(args)
        command = join(args, ' ')
        return TreeHandle(fh, command)

    def get_revision_info(self, rev):
        properties = { }
        for property_name in [ 'svn:author', 'svn:date', 'svn:log' ]:
            with CheckedCommandFileHandle([ 'svnlook', 'pg', '--revprop', '-r', str(rev), self.path, property_name]) as fh:
                properties[property_name] = fh.read()
        return RevisionInfo(
            author = properties['svn:author'],
            date = properties['svn:date'],
            log_message = properties['svn:log'],
        )

    def get_uuid(self):
        with CheckedCommandFileHandle([ 'svnlook', 'uuid', self.path ]) as fh:
            line = fh.read()
        return line[:-1]

    def get_youngest_revision(self):
        with CheckedCommandFileHandle([ 'svnlook', 'youngest', self.path ]) as fh:
            line = fh.read()
        return int(line[:-1])
