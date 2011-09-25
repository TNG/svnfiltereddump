
from SvnDumpReader import SvnDumpReader
from LumpBuilder import LumpBuilder

class DumpFilter(object):
    def __init__(self, config, source_repository, interesting_paths, dump_writer):
        self.config = config
        self.source_repository = source_repository
        self.interesting_paths = interesting_paths
        self.dump_writer = dump_writer
        self.dump_reader = None
        self.revision_header = None
        self.revision_header_dumped = False
        self.revision_number = None
        self.lump_builder = LumpBuilder(source_repository)

    def filter_revision(self, revision):
        input_fh = self.source_repository.get_dump_file_handle_for_revision(revision)
        self.dump_reader = SvnDumpReader(input_fh)
        self._process_header_lumps()

        while True:
            lump = self.dump_reader.read_lump()
            if lump is None:
                break;
            self._process_lump(lump) 

        self._flush()
        self.dump_reader = None

    def _process_header_lumps(self):
        lump = self.dump_reader.read_lump()
        while lump and not lump.has_header('Revision-number'):
            lump = self.dump_reader.read_lump()
        if not lump:
            raise Exception("Failed to parse dump of revision %d: No revision header found!")
        self.revision_header = lump
        self.revision_header_dumped = False 
        self.revision_number = int(lump.get_header('Revision-number'))

    def _flush(self):
        if not self.revision_header_dumped and not self.config.drop_empty_revs:
            self._write_revision_header()
        self.revision_header = None

    def _write_revision_header(self):
        self.dump_writer.write_lump(self.revision_header)
        self.revision_header_dumped = True

    def _process_lump(self, lump):
        action = lump.get_header('Node-action')
        if action == 'add':
            self._process_add_lump(lump)
        elif action == 'delete':
            self._process_delete_lump(lump)
        elif action == 'change':
            self._process_change_lump(lump)
        else:
            raise Exception("Unknown Node-action '%'!" % ( action ) )

    def _process_add_lump(self, lump):
        path = lump.get_header('Node-path')
        if not self.interesting_paths.is_interesting(path):
            return

        if not lump.has_header('Node-copyfrom-path'):
            self._write(lump)
            return

        from_path = lump.get_header('Node-copyfrom-path')
        from_rev = int(lump.get_header('Node-copyfrom-rev'))

        start_rev = 0
        if self.config.start_rev:
            start_rev = self.config.start_rev
        is_internal_copy = self.interesting_paths.is_interesting(from_path) and from_rev >= start_rev
        if is_internal_copy:
            self._write(lump)
        else:
            node_kind = lump.get_header('Node-kind')
            self._copy_path_from_source(path, from_path, from_rev, node_kind)
            if lump.content:
                new_lump = self.lump_builder.change_lump_from_add_lump(lump)
                self._write(new_lump)
                
    def _copy_path_from_source(self, path, from_path, from_rev, node_kind):
        if node_kind == 'file':
            new_lump = self.lump_builder.add_path_from_source_repository('file', path, from_path, from_rev)
            self._write(new_lump)
            return

        if path[-1:] != '/':
            path += '/'
        with self.source_repository.get_tree_handle_for_path(from_path, from_rev) as tree_handle:
            for from_sub_path in tree_handle:
                if from_sub_path[-1:] == '/':
                    kind = 'dir'
                    from_sub_path = from_sub_path[:-1]
                else:
                    kind = 'file'
                sub_path = path + from_sub_path[len(from_path):]
                new_lump = self.lump_builder.add_path_from_source_repository(kind, sub_path, from_sub_path, from_rev)
                self._write(new_lump)

    def _process_delete_lump(self, lump):
        path = lump.get_header('Node-path')
        if self.interesting_paths.is_interesting(path):
            self._write(lump)
            return

        paths_to_check = self.interesting_paths.get_interesting_sub_directories(path)
        if not paths_to_check:
            return
        previous_revision = self.revision_number - 1
        for path_to_check in paths_to_check:
            does_exist = self.source_repository.get_type_of_path(path_to_check, previous_revision) is not None
            if does_exist:
                new_lump = self.lump_builder.delete_path(path_to_check)
                self._write(new_lump)

    def _process_change_lump(self, lump):
        path = lump.get_header('Node-path')
        if self.interesting_paths.is_interesting(path):
            self._write(lump)

    def _write(self, lump):
        if not self.revision_header_dumped:
            self._write_revision_header()
        self.dump_writer.write_lump(lump)
