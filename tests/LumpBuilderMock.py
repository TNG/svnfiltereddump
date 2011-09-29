
from copy import copy
from StringIO import StringIO

class LumpBuilderMock(object):
    def __init__(self):
        self.call_history = [ ]
    def delete_path(self, path):
        self.call_history.append( [ 'delete_path', path ] )
    def add_path_from_source_repository(self, kind, path, source_path, source_rev):
        self.call_history.append( [ 'add_path_from_source_repository',  kind, path, source_path, source_rev ] )
    def change_lump_from_add_lump(self, lump):
        self.call_history.append( [ 'change_lump_from_add_lump', self._clone_lump_to_lump_with_fake_bin(lump) ] )
    def revision_header(self, rev):
        self.call_history.append( [ 'revision_header', rev ] )
    def dump_header_lumps(self):
        self.call_history.append( [ 'dump_header_lumps' ] )
    def revision_header(self, rev):
        self.call_history.append( [ 'revision_header', rev ] )
    def pass_lump(self, lump):
        self.call_history.append( [ 'pass_lump', self._clone_lump_to_lump_with_fake_bin(lump) ] )
    def add_tree_from_source(self, path, source_path, source_rev):
         self.call_history.append( [ 'add_tree_from_source', path, source_path, source_rev ] )
    def _clone_lump_to_lump_with_fake_bin(self, lump):
        new_lump = copy(lump)
        if lump.content:
            fh = StringIO()
            lump.content.empty_to(fh)
            fh.seek(0)
            new_lump.content = fh.read()
        return new_lump
        
        
