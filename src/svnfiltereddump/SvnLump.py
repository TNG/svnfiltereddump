
from ordereddict import OrderedDict

class SvnLump:

    def __init__(self):
        self.headers = OrderedDict()
        self.properties = { }
        self.content = None

    def set_header(self, key, value):
        self.headers[key] = value

    def get_header(self, key):
        return self.headers[key]

    def delete_header(self, key):
        del self.headers[key]

    def get_header_keys(self):
        return self.headers.keys()
