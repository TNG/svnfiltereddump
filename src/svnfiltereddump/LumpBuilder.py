
from os.path import normpath
from copy import copy

from SvnLump import SvnLump
from SvnRepository import SvnRepository

class LumpBuilder(object):
    def __init__(self, source_repository, interesting_paths, dump_writer):
        self.source_repository = source_repository
        self.interesting_paths = interesting_paths
        self.dump_writer = dump_writer

    def delete_path(self, path):
        lump = SvnLump()
        lump.set_header('Node-path', normpath(path))
        lump.set_header('Node-action', 'delete')
        self.dump_writer.write_lump(lump)

    def mkdir(self, path):
        lump = SvnLump()
        lump.set_header('Node-path', normpath(path))
        lump.set_header('Node-kind', 'dir')
        lump.set_header('Node-action', 'add')
        self.dump_writer.write_lump(lump)

    def add_path_from_source_repository(self, kind, path, from_path, from_rev):
        assert kind == 'file' or kind =='dir'

        path = normpath(path)
        repo = self.source_repository
        lump = SvnLump()

        lump.set_header('Node-path', path)
        lump.set_header('Node-kind', kind)
        lump.set_header('Node-action', 'add')

        if kind == 'file':
            tin = repo.get_tin_for_file(from_path, from_rev)
            lump.content = tin
            lump.set_header('Text-content-length', str(tin.size))
            lump.set_header('Text-content-md5', tin.md5sum)

        lump.properties = repo.get_properties_of_path(from_path, from_rev)
        self.dump_writer.write_lump(lump)

    def change_lump_from_add_lump(self, sample_lump):
        lump = copy(sample_lump)
        lump.set_header('Node-action', 'change')
        for header_name in [
            'Node-kind', 'Node-copyfrom-path', 'Node-copyfrom-rev',
            'Text-copy-source-md5', 'Text-copy-source-sha1'
        ]:
            if lump.has_header(header_name):
                lump.delete_header(header_name)
        self.dump_writer.write_lump(lump)

    def revision_header(self, rev):
        lump = SvnLump()
        lump.set_header('Revision-number', str(rev))
        rev_info = self.source_repository.get_revision_info(rev)
        lump.properties = {
            'svn:author': rev_info.author,
            'svn:date': rev_info.date,
            'svn:log': rev_info.log_message
        }
        self.dump_writer.write_lump(lump)

    def dump_header_lumps(self):
        lump = SvnLump()
        lump.set_header('SVN-fs-dump-format-version', '2')
        self.dump_writer.write_lump(lump)

        lump = SvnLump()
        lump.set_header('UUID', str(self.source_repository.get_uuid()))
        self.dump_writer.write_lump(lump)

    def pass_lump(self, lump):
        self.dump_writer.write_lump(lump)

    def add_tree_from_source(self, path, from_path, from_rev):
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
                if self.interesting_paths.is_interesting(sub_path):
                    self.add_path_from_source_repository(kind, sub_path, from_sub_path, from_rev)
