
from optparse import OptionParser
from string import join

VERSION = '1.0 Beta4'

def _parse_command_line(command_line):
    parser = OptionParser("usage: %prog [options] <absolute repository path> <include path> ...\n\nVersion " + VERSION)
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
        '--keep-empty-revs', action='store_true', dest='keep_empty_revs', default=False,
        help="Copy revisions even if they have no effect on included paths at all."
    )
    parser.add_option(
        '--start-rev', dest='start_rev', type='int',
        help="Squash the revision history below the given revision. Generate artificial first revision with represents the given input revision.",
        metavar='NUMBER'
    )
    parser.add_option(
        '--no-extra-mkdirs', action='store_false', dest='create_parent_dirs', default=True,
        help="By default extra nodes are injected to create the parent directories of all paths in the include list. Use this option to switch it off."
    )
    parser.add_option(
        '--drop-old-tags-and-branches', action='store_true', dest='drop_old_tags_and_branches', default=False,
        help="Use with the --start-rev option. Automatically exclude data in tags and branches directories referring to data before and up to the start revision."
    )
    parser.add_option(
        '--tag-or-branch-dir', action='append', dest='custom_tags_and_branches_dirs', default=[],
        help='Use with --drop-old-tags-and-branches. Overwrites the list of directory names, which contain tags and branches in your repository. Add one --tag-or-branch-dir option for each name you want - including \'tags\' and \'branches\' if you want to extend the original list.',
        metavar='NAME'
    )
    parser.add_option(
        '--trunk-dir', action='append', dest='custom_trunk_dirs', default=[],
        help='Use with --drop-old-tags-and-branches. Overwrites the list of directory names, which contain the trunk(s) your repository. Add one --tuunk-dir option for each name you want - including \'trunk\' if you want to extend the original list.',
        metavar='NAME'
    )
    parser.add_option(
        '-q', '--quiet', action='store_true', dest='quiet', default=False,
        help="Only log errors and warnings on console."
    )
    parser.add_option(
        '-l', '--log-file', dest='log_file',
        help="Write messages to given log file.",
        metavar='FILE'
    )

    (options, args ) =  parser.parse_args(command_line) 

    if len(args) < 1:
        parser.error('No repository given!')
    source_repository = args[0]
    if not source_repository.startswith('/'):
        parser.error('Please supply ABSOLUTE path to repository!')

    include_paths = [ ]
    for path in args[1:]:
        if path[0] == '/':
            include_paths.append(path[1:])
        else:
            include_paths.append(path)

    return ( options, source_repository, include_paths )
    

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
        ( options, source_repository, include_paths ) = _parse_command_line(command_line)

        self.source_repository = source_repository

        for file in options.include_files:
            include_paths += _get_file_as_list(file)
        self.include_paths = include_paths

        exclude_paths = options.exclude_paths
        for file in options.exclude_files:
            exclude_paths += _get_file_as_list(file)
        self.exclude_paths = exclude_paths

        self.keep_empty_revs = options.keep_empty_revs
        self.start_rev = options.start_rev
        self.create_parent_dirs = options.create_parent_dirs
        self.quiet = options.quiet
        self.log_file = options.log_file

        self.drop_old_tags_and_branches = options.drop_old_tags_and_branches

        if options.custom_tags_and_branches_dirs:
            self.tag_and_branch_dict = { }
            for name in options.custom_tags_and_branches_dirs:
                self.tag_and_branch_dict[name] = True
        else:
            self.tag_and_branch_dict = { 'tags': True, 'branches': True }
        self.trunk_dict = { }
        if options.custom_trunk_dirs:
            self.trunk_dict = { }
            for name in options.custom_trunk_dirs:
                self.trunk_dict[name] = True
        else:
            self.trunk_dict = { 'trunk':True }

    def is_path_tag_or_branch(self, path):
        is_just_below_tags_or_branches = False
        is_tag_or_branch = False
        for element in path.split('/'):
            if element == '':
                continue
            if self.trunk_dict.has_key(element):
                return False
            elif self.tag_and_branch_dict.has_key(element):
                is_just_below_tags_or_branches = True
            elif is_just_below_tags_or_branches:
                is_just_below_tags_or_branches = False
                is_tag_or_branch = True
            elif is_tag_or_branch:
                return False
        return is_tag_or_branch
