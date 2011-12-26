
class BootsTrapper(object):
    def __init__(self, config, source_repository, interesting_paths, lump_builder):
        self.config = config
        self.source_repository = source_repository
        self.interesting_paths =interesting_paths
        self.lump_builder = lump_builder

    def process_revision(self, revision, aux_data):
        assert aux_data is None
        builder = self.lump_builder
        builder.revision_header(revision, 'svnfiltereddump boots trap revision')
        paths_of_interest = sorted(self.interesting_paths.get_interesting_sub_directories(''))
        for path in paths_of_interest:
            kind = self.source_repository.get_type_of_path(path, revision)
            if kind:
                builder.get_recursively_from_source(kind, path, 'add', path, revision)    
