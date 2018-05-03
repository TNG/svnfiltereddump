from StringIO import StringIO
from svnfiltereddump import ContentTin


class _FakeIterator(object):
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return self

    def next(self):
        if len(self.items):
            next_item = self.items[0]
            self.items = self.items[1:]
            return next_item
        else:
            raise StopIteration()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        return False


class RevisionInfo(object):
    def __init__(self, author, date, log_message):
        self.author = author
        self.date = date
        self.log_message = log_message


class RepositoryMock(object):
    def __init__(self):
        self.dumps_by_revision = {}
        self.files_by_name_and_revision = {}
        self.properties_by_path_and_revision = {}
        self.tree_by_path_and_revision = {}
        self.revision_properties_by_revision = {}

    def get_tin_for_file(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        content = self.files_by_name_and_revision[path][rev]
        fh = StringIO(content)
        return ContentTin(fh, len(content), 'FAKEMD5')

    def get_properties_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        return self.properties_by_path_and_revision[path][rev]

    def get_type_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        if path in self.files_by_name_and_revision and rev in self.files_by_name_and_revision[path]:
            return 'file'
        if path in self.tree_by_path_and_revision and rev in self.tree_by_path_and_revision[path]:
            return 'dir'
        return None

    def get_tree_handle_for_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        return _FakeIterator(self.tree_by_path_and_revision[path][rev])

    def get_dump_file_handle_for_revision(self, rev):
        return StringIO(self.dumps_by_revision[rev])

    def get_revision_info(self, rev):
        author, date, log = self.revision_properties_by_revision[rev]
        return RevisionInfo(author, date, log)

    @staticmethod
    def get_uuid():
        return 'fake-uuid'
