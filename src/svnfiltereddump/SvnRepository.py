
from subprocess import Popen, check_call, PIPE, STDOUT
from CheckedCommandFileHandle import CheckedCommandFileHandle

class SvnRepository(object):

    def __init__(self, path):
        self.path = path

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
