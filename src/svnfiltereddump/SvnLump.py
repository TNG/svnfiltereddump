
class SvnLump:

    def __init__(self):
        self.headers = { }
        self.header_order = [ ]
        self.properties = { }
        self.content = None

    def set_header(self, key, value):
        if not self.headers.has_key(key):
            self.header_order.append(key)
        self.headers[key] = value

    def get_header(self, key):
        return self.headers[key]

    def has_header(self, key):
        return self.headers.has_key(key)

    def delete_header(self, key):
        del self.headers[key]
        self.header_order.remove(key)

    def get_header_keys(self):
        return self.header_order
