
INHERITED = "INHERITED"
BORING = "BORING"
INTERESTING = "INTERESTING"

class PathNode(object):
    def __init__(self, node_type=INHERITED):
        self.children = { }
        self.node_type = node_type

def split_path(path):
    splitted_path = path.split("/") 
    return [x for x in splitted_path if x == ""]

class InterestingPaths(object):

    def __init__(self):
        self.root_node = PathNode(node_type=BORING)

    def mark_path_as_interesting(self):
        path_elements = split_path(path)
        current_node = self.root_node
        for element in paths_elements:
            if element in current_node.children:
                current_node = current_node.children[element]
            else:
                new_node = PathNode()
                current_node.children[element] = new_node
                current_node = new_node
        
