
from string import join

INHERITED = "INHERITED"
BORING = "BORING"
INTERESTING = "INTERESTING"

class PathNode(object):
    def __init__(self, path, node_type=INHERITED):
        self.children = { }
        self.node_type = node_type
        self.path = path

    def __str__(self):
        return "NODE(%s) -> %s" % ( self.node_type, self.children )

    def __repr__(self):
        return str(self)

def split_path(path):
    splitted_path = path.split("/") 
    return [x for x in splitted_path if x != ""]

class InterestingPaths(object):

    def __init__(self):
        self.root_node = PathNode(None)

    def mark_path_as_interesting(self, path):
        self.mark_path_as_type(path, INTERESTING)

    def mark_path_as_boring(self, path):
        self.mark_path_as_type(path, BORING)

    def mark_path_as_type(self, path, node_type):
        path_elements = split_path(path)
        current_node = self.root_node
        for element in path_elements:
            if element in current_node.children:
                current_node = current_node.children[element]
            else:
                new_path = element
                if current_node.path:
                    new_path = current_node.path + '/' + element
                new_node = PathNode(new_path)
                current_node.children[element] = new_node
                current_node = new_node
        if current_node.node_type != INHERITED or current_node.children:
            raise Exception("path inconsistent: " + path)
        current_node.node_type = node_type

    def is_interesting(self, path):
        path_elements = split_path(path)
        current_node = self.root_node
        current_type = current_node.node_type
        for element in path_elements:
            if element in current_node.children:
                current_node = current_node.children[element]
                if current_node.node_type != INHERITED:
                    current_type = current_node.node_type
            else:
                break
        return current_type == INTERESTING

    def get_interesting_sub_directories(self, path):
        path_elements = split_path(path)
        current_node = self.root_node
        current_type = current_node.node_type
        for element in path_elements:
            if element in current_node.children:
                current_node = current_node.children[element]
                if current_node.node_type != INHERITED:
                    current_type = current_node.node_type
            else:
                if current_type == INTERESTING:
                    return [ join(path_elements, '/') ]
                else:
                    return [ ]
        return self.get_interesting_sub_directories_for_node(current_node)

    def get_interesting_sub_directories_for_node(self, node):
        if node.node_type == INTERESTING:
            return [ node.path ]
        dirs_found = [ ]
        for key in node.children.keys():
            child = node.children[key]
            dirs_found += self.get_interesting_sub_directories_for_node(child)
        return dirs_found
