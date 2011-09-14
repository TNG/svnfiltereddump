
from optparse import OptionParser

def _parse_command_line(command_line):
    parser = OptionParser()
    parser.add_option(
        '--include-file', action='append', dest='include_files', default=[],
        help='Read paths to include from given file.',
        metavar='FILE'
    )
    parser.add_option(
        '--exclude', action='append', dest='exclude_paths', default=[],
        help='Exclude given path during filtering.',
        metavar='PATH'
    )
    parser.add_option(
        '--exclude-file', action='append', dest='exclude_files', default=[],
        help='Read paths to exclude from given file.',
        metavar='FILE'
    )
    parser.add_option(
        '--drop-empty-revs', action='store_true', dest='drop_empty_revs', default=False,
        help="Drop revisions with no effect on included paths completely. ",
    )
    parser.add_option(
        '--renumber-revs', action='store_true', dest='renumber_revs', default=False,
        help="Renumber revisions - makes only sense with --drop-empty-revs.",
    )
    parser.add_option(
        '--start-rev', dest='start_rev', type='int',
        help="Squash the revision history below the given revision. Generate artificial first revision with represents the given input revision.",
        metavar='NUMBER'
    )

    return  parser.parse_args(command_line) 

def _get_file_as_list(name):
    list = [ ]
    fh = open(name, 'r')
    for line in fh:
        if line[-1:] == "\n":
            line = line[:-1]
        list.append(line)
    return list
        
class Config(object):

    def __init__(self, command_line):
        ( options, args ) = _parse_command_line(command_line)
        include_paths = args
        exclude_paths = options.exclude_paths
        for file in options.include_files:
            include_paths += _get_file_as_list(file)
        for file in options.exclude_files:
            exclude_paths += _get_file_as_list(file)

        self.include_paths = include_paths
        self.exclude_paths = exclude_paths
        self.drop_empty_revs = options.drop_empty_revs
        self.renumber_revs = options.renumber_revs
        self.start_rev = options.start_rev
