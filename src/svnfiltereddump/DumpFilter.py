
from logging import info
from SvnDumpReader import SvnDumpReader
from LumpBuilder import LumpBuilder

class UnsupportedDumpVersionException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DumpFilter(object):
    def __init__(self, config, source_repository, interesting_paths, lump_builder):
        self.config = config
        self.source_repository = source_repository
        self.interesting_paths = interesting_paths
        self.dump_reader = None
        self.revision_number = None
        self.lump_builder = lump_builder

    def process_revision(self, revision, aux_data):
        assert aux_data is None
        input_fh = self.source_repository.get_dump_file_handle_for_revision(revision)
        self.dump_reader = SvnDumpReader(input_fh)
        self._process_header_lumps()

        while True:
            lump = self.dump_reader.read_lump()
            if lump is None:
                break;
            self._process_lump(lump) 

        self.dump_reader = None

    def _process_header_lumps(self):
        lump = self.dump_reader.read_lump()
        while lump and not lump.has_header('Revision-number'):
            self._validate_dump_header_lump(lump)
            lump = self.dump_reader.read_lump()
        if not lump:
            raise Exception("Failed to parse dump of revision %d: No revision header found!")
        self.revision_number = int(lump.get_header('Revision-number'))
        self.lump_builder.pass_lump(lump)

    def _validate_dump_header_lump(self, lump):
        if lump.has_header('SVN-fs-dump-format-version'):
            dump_format_version = lump.get_header('SVN-fs-dump-format-version')
            if dump_format_version != '2':
                raise UnsupportedDumpVersionException(
                    'Detected unsupported SVN version - SVN-fs-dump-format-version was %s (wanted: 2)'
                    % ( dump_format_version )
                )

    def _process_lump(self, lump):
        action = lump.get_header('Node-action')
        if action == 'add' or action == 'replace':
            self._process_add_or_replace_lump(lump, action)
        elif action == 'delete':
            self._process_delete_lump(lump)
        elif action == 'change':
            self._process_change_lump(lump)
        else:
            raise Exception("Unknown Node-action '%s'!" % ( action ) )

    def _process_add_or_replace_lump(self, lump, action):
        path = lump.get_header('Node-path')
        if self.interesting_paths.is_interesting(path):
            self._process_add_or_replace_lump_of_interesting_path(lump, action)
            return

        if lump.get_header('Node-kind') != 'dir':
            return
        if not lump.has_header('Node-copyfrom-path'):
            return

        from_path = lump.get_header('Node-copyfrom-path')
        from_rev = int(lump.get_header('Node-copyfrom-rev'))
        self._add_or_replace_interesting_sub_directories_of_path(path, action, from_path, from_rev)

    def _process_add_or_replace_lump_of_interesting_path(self, lump, action):
        path = lump.get_header('Node-path')
        if not lump.has_header('Node-copyfrom-path'):
            self.lump_builder.pass_lump(lump)
            return

        from_path = lump.get_header('Node-copyfrom-path')
        from_rev = int(lump.get_header('Node-copyfrom-rev'))

        if self._is_internal_copy(from_path, from_rev):
            self.lump_builder.pass_lump(lump)
        else:
            node_kind = lump.get_header('Node-kind')
            self.lump_builder.get_recursively_from_source(node_kind, path, action, from_path, from_rev)
            if lump.content:
                self.lump_builder.change_lump_from_add_or_replace_lump(lump)

    def _is_internal_copy(self, from_path, from_rev):
        if self.config.start_rev and from_rev <  self.config.start_rev:
            return False
        return self.interesting_paths.is_interesting(from_path)

    def _add_or_replace_interesting_sub_directories_of_path(self, path, action, from_path, from_rev):
        if path[-1:] == '/':
            path = path[:-1]
        paths_to_check = self.interesting_paths.get_interesting_sub_directories(path)
        for sub_path in paths_to_check:
            from_sub_path = from_path + sub_path[len(path):]
            node_kind = self.source_repository.get_type_of_path(from_sub_path, from_rev)
            if not node_kind:
                continue
            if self._is_internal_copy(from_sub_path, from_rev):
                self.lump_builder.get_path_from_target(node_kind, sub_path, action, from_sub_path, from_rev)
            else:
                self.lump_builder.get_recursively_from_source(node_kind, sub_path, action, from_sub_path, from_rev)

    def _process_delete_lump(self, lump):
        path = lump.get_header('Node-path')
        if self.interesting_paths.is_interesting(path):
            self.lump_builder.pass_lump(lump)
            return

        paths_to_check = self.interesting_paths.get_interesting_sub_directories(path)
        if not paths_to_check:
            return
        previous_revision = self.revision_number - 1
        for path_to_check in paths_to_check:
            does_exist = self.source_repository.get_type_of_path(path_to_check, previous_revision) is not None
            if does_exist:
                self.lump_builder.delete_path(path_to_check)

    def _process_change_lump(self, lump):
        path = lump.get_header('Node-path')
        if self.interesting_paths.is_interesting(path):
            self.lump_builder.pass_lump(lump)


