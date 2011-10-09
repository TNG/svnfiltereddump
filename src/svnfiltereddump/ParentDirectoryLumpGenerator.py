
from string import join

class ParentDirectoryLumpGenerator(object):

    def __init__(self, interesting_paths, lump_builder):
        self.interesting_paths = interesting_paths
        self.lump_builder = lump_builder

    def write_lumps(self):
        paths_to_create_by_length = self._claculate_paths_to_create_by_length()
        for paths_to_create in paths_to_create_by_length:
            for path in paths_to_create:
                self.lump_builder.mkdir(path)

    def _claculate_paths_to_create_by_length(self):
        hashed_paths_by_length = [ None ]
        all_interesting_paths = self.interesting_paths.get_interesting_sub_directories('')
        for path in all_interesting_paths:
            parent_path_elements = path.split('/')[:-1]
            for prefix_length in range(1, len(parent_path_elements)+1):
                prefix = join(parent_path_elements[:prefix_length], '/')
                if prefix_length == len(hashed_paths_by_length):
                    hashed_paths_by_length.append( { prefix: True } )
                else:
                    hashed_paths_by_length[prefix_length][prefix] = True

        paths_by_prefix_length = [ [] ]
        for hashed_paths in hashed_paths_by_length[1:]:
            paths_by_prefix_length.append(sorted(hashed_paths.keys())) # Sorted for easier testing
        return paths_by_prefix_length
