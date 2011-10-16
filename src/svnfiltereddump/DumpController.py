
from logging import info

STRATEGY_DUMP_HEADER = 'DUMP_HEADER'
STRATEGY_IGNORE = 'IGNORE'
STRATEGY_SYNTHETIC_DELETES = 'SYNTHETIC_DELETES'
STRATEGY_DUMP_SCAN = 'DUMP_SCAN'
STRATEGY_BOOTSTRAP = 'BOOTSTRAP'

DUMP_HEADER_PSEUDO_REV = -1

class DumpController(object):
    def __init__(self, config, repository, interesting_paths, revision_handlers_by_strategy):
        self.config = config
        self.repository = repository
        self.interesting_paths = interesting_paths
        self.revision_handlers_by_strategy = revision_handlers_by_strategy

    def _get_strategy_and_aux_data_for_revision(self, rev):
        if rev == DUMP_HEADER_PSEUDO_REV:
            return ( STRATEGY_DUMP_HEADER, None )
        if rev == self.config.start_rev:
            return ( STRATEGY_BOOTSTRAP, None )

        changes_by_type = self.repository.get_changed_paths_by_change_type_for_revision(rev)

        for change_type in changes_by_type.keys():
            if change_type == 'D':
                continue
            for path in changes_by_type[change_type]:
                if self.interesting_paths.is_interesting(path):
                    return ( STRATEGY_DUMP_SCAN, None )
                if change_type == 'A':
                    if self.interesting_paths.get_interesting_sub_directories(path):
                        return ( STRATEGY_DUMP_SCAN, None )

        if not changes_by_type.has_key('D'):
            return ( STRATEGY_IGNORE, None )

        delete_paths = [ ]
        for path in changes_by_type['D']:
            delete_paths += self.interesting_paths.get_interesting_sub_directories(path)
        if delete_paths:
            return ( STRATEGY_SYNTHETIC_DELETES, delete_paths )
       
        return ( STRATEGY_IGNORE, None )

    def run(self):
        header_handler = self.revision_handlers_by_strategy[STRATEGY_DUMP_HEADER]
        header_handler.process_revision(DUMP_HEADER_PSEUDO_REV, None)

        first_revision = 1
        if self.config.start_rev:
            first_revision = self.config.start_rev
        last_revision = self.repository.get_youngest_revision()

        for revision in xrange(first_revision, last_revision+1):
            ( strategy, aux_data ) = self._get_strategy_and_aux_data_for_revision(revision)
            info("Processing input revsion %d using strategy %s ..." % ( revision, strategy ) )
            handler = self.revision_handlers_by_strategy[strategy]
            handler.process_revision(revision, aux_data) 
