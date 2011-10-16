
INHERITED = "INHERITED"
BORING = "BORING"
INTERESTING = "INTERESTING"

class _PathNode(object):
    def __init__(self, path, node_type=INHERITED):
        self.children = { }
        self.node_type = node_type
        self.path = path

    def add_child(self, name):
        if self.path:
            path = self.path + '/' + name
        else:
            path = name
        child = _PathNode(path)
        self.children[name] = child
        return child

    def __str__(self):
        return "NODE(%s) -> %s" % ( self.node_type, self.children )

    def __repr__(self):
        return str(self)

def split_path(path):
    splitted_path = path.split("/") 
    return [x for x in splitted_path if x != ""]

class InterestingPaths(object):

    def __init__(self):
        self.root_node = _PathNode(None)

    def mark_path_as_interesting(self, path):
        self._mark_path_as_type(path, INTERESTING)

    def mark_path_as_boring(self, path):
        self._mark_path_as_type(path, BORING)

    def _mark_path_as_type(self, path, node_type):
        path_elements = split_path(path)
        current_node = self.root_node
        for element in path_elements:
            if element in current_node.children:
                current_node = current_node.children[element]
            else:
                current_node = current_node.add_child(element)
        if current_node.node_type != INHERITED or current_node.children:
            raise Exception("path inconsistent: " + path)
        current_node.node_type = node_type

    def is_interesting(self, path):
        ( node, node_type ) = self._get_node_and_type_of_path(path)
        return node_type == INTERESTING

    def _get_node_and_type_of_path(self, path):
        path_elements = split_path(path)
        current_node = self.root_node
        current_type = current_node.node_type
        for element in path_elements:
            if element in current_node.children:
                current_node = current_node.children[element]
                if current_node.node_type != INHERITED:
                    current_type = current_node.node_type
            else:
                current_node = None
                break
        return ( current_node, current_type )

    def get_interesting_sub_directories(self, path):
        ( node, node_type ) = self._get_node_and_type_of_path(path)
        if node_type == INTERESTING:
            return [ path ]
        if node is None:
            return [ ]
        return self._get_interesting_sub_directories_for_node(node)

    def _get_interesting_sub_directories_for_node(self, node):
        if node.node_type == INTERESTING:
            return [ node.path ]
        dirs_found = [ ]
        for key in node.children.keys():
            child = node.children[key]
            dirs_found += self._get_interesting_sub_directories_for_node(child)
        return dirs_found
