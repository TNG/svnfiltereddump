from copy import copy
from StringIO import StringIO


class LumpBuilderMock(object):
    def __init__(self):
        self.call_history = []

    def delete_path(self, path):
        self.call_history.append(['delete_path', path])

    def mkdir(self, path):
        self.call_history.append(['mkdir', path])

    def get_node_from_source(self, kind, path, action, source_path, source_rev):
        self.call_history.append(['get_node_from_source',  kind, path, action, source_path, source_rev])

    def change_lump_from_add_or_replace_lump(self, lump):
        self.call_history.append(['change_lump_from_add_or_replace_lump', self._clone_lump_to_lump_with_fake_bin(lump)])

    def dump_header_lumps(self):
        self.call_history.append(['dump_header_lumps'])

    def revision_header(self, rev, log='None'):
        self.call_history.append(['revision_header', rev, log])

    def pass_lump(self, lump):
        self.call_history.append(['pass_lump', self._clone_lump_to_lump_with_fake_bin(lump)])

    def get_recursively_from_source(self, kind, path, action, source_path, source_rev):
        self.call_history.append(['get_recursively_from_source', kind, path, action, source_path, source_rev])

    def get_path_from_target(self, kind, path, action, from_path, from_rev):
        self.call_history.append(['get_path_from_target', kind, path, action, from_path, from_rev])

    @staticmethod
    def _clone_lump_to_lump_with_fake_bin(lump):
        new_lump = copy(lump)
        if lump.content:
            fh = StringIO()
            lump.content.empty_to(fh)
            fh.seek(0)
            new_lump.content = fh.read()
        return new_lump
