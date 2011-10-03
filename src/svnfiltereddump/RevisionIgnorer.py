
class RevisionIgnorer(object):
    def __init__(self, lump_builder):
        self.lump_builder = lump_builder

    def process_revision(self, rev, aux_data):
        assert aux_data is None
        builder = self.lump_builder
        builder.revision_header(rev)
