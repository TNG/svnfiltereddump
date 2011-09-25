
from os.path import normpath
from copy import copy

from SvnLump import SvnLump
from SvnRepository import SvnRepository

class LumpBuilder(object):
    def __init__(self, source_repository):
        self.source_repository = source_repository

    def delete_path(self, path):
        lump = SvnLump()
        lump.set_header('Node-path', normpath(path))
        lump.set_header('Node-action', 'delete')
        return lump

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
        return lump

    def change_lump_from_add_lump(self, sample_lump):
        lump = copy(sample_lump)
        lump.set_header('Node-action', 'change')
        for header_name in [
            'Node-kind', 'Node-copyfrom-path', 'Node-copyfrom-rev',
            'Text-copy-source-md5', 'Text-copy-source-sha1'
        ]:
            if lump.has_header(header_name):
                lump.delete_header(header_name)
        return lump

    def revision_header(self, rev):
        lump = SvnLump()
        lump.set_header('Revision-number', str(rev))
        rev_info = self.source_repository.get_revision_info(rev)
        lump.properties = {
            'svn:author': rev_info.author,
            'svn:date': rev_info.date,
            'svn:log': rev_info.log_message
        }
        return lump

    def dump_header_lumps(self):
        format_lump = SvnLump()
        format_lump.set_header('SVN-fs-dump-format-version', '2')
        uuid_lump = SvnLump()
        uuid_lump.set_header('UUID', str(self.source_repository.get_uuid()))
        return [ format_lump, uuid_lump ]
