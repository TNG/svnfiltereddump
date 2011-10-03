
from DumpController import DUMP_HEADER_PSEUDO_REV
class DumpHeaderGenerator(object):
    def __init__(self, lump_builder):
        self.lump_builder = lump_builder

    def process_revision(self, rev, aux_data):
        assert rev == DUMP_HEADER_PSEUDO_REV
        assert aux_data is None
        builder = self.lump_builder
        builder.dump_header_lumps()
