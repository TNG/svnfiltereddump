
STRATEGY_IGNORE = 'IGNORE'
STRATEGY_SYNTHETIC_DELETES = 'SYNTHETIC_DELETES'
STRATEGY_DUMP_SCAN = 'DUMP_SCAN'

class RevisionAnalyser(object):
    def __init__(self, repository, intresting_paths):
        self.repository = repository
        self.intresting_paths = intresting_paths

    def get_strategy_and_delete_paths_for_revision(self, rev):
        changes_by_type = self.repository.get_changed_paths_by_change_type_for_revision(rev)

        for change_type in changes_by_type.keys():
            if change_type == 'D':
                continue
            for path in changes_by_type[change_type]:
                if self.intresting_paths.is_interesting(path):
                    return ( STRATEGY_DUMP_SCAN, None )

        if not changes_by_type.has_key('D'):
            return ( STRATEGY_IGNORE, None )

        delete_paths = [ ]
        for path in changes_by_type['D']:
            delete_paths += self.intresting_paths.get_interesting_sub_directories(path)
        if delete_paths:
            return ( STRATEGY_SYNTHETIC_DELETES, delete_paths )
       
        return ( STRATEGY_IGNORE, None )
