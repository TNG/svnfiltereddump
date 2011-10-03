
class SyntheticDeleter(object):
    def __init__(self, source_repository, lump_builder):
        self.source_repository = source_repository
        self.lump_builder = lump_builder

    def process_revision(self, rev, deleted_paths):
        builder = self.lump_builder
        previous_revision = rev - 1
        builder.revision_header(rev)
        for path in deleted_paths:
            kind = self.source_repository.get_type_of_path(path, previous_revision)
            if kind:
                builder.delete_path(path)
