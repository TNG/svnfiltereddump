
from unittest import TestCase
from StringIO import StringIO

from svnfiltereddump import SvnLump, LumpBuilder, ContentTin, InterestingPaths

from DumpWriterMock import DumpWriterMock

class FakeIterator(object):
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
        pass

class RevisionInfoMock:
    def __init__(self):
        self.author = 'testuser'
        self.date = 'some date'
        self.log_message = 'log message'

class SvnRepositoryMock(object):

    def get_tin_for_file(self, path, rev):
        if path == 'file/in/source/repo_rev17' and rev == 17:
            fh = StringIO('xxxXXX')
            return ContentTin(fh, 3, 'FAKESUM')
        elif path == 'dir/in/source/repo_rev2/x' and rev == 2:
            fh = StringIO('xXXX')
            return ContentTin(fh, 1, 'FAKESUM')
        elif path == 'dir/in/source/repo_rev2/y' and rev == 2:
            fh = StringIO('yXXX')
            return ContentTin(fh, 1, 'FAKESUM')
        else:
            assert False

    def get_properties_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        if path == 'file/in/source/repo_rev17' and rev == 17:
            return { 'a': 'x1', 'b': 'x2' }
        elif path == 'dir/in/source/repo_rev2' and rev == 2:
            return { 'a2': 'y1', 'b2': 'y2' }
        elif path == 'dir/in/source/repo_rev2/x' and rev == 2:
            return { }
        elif path == 'dir/in/source/repo_rev2/y' and rev == 2:
            return { }
        else:   
            assert False

    def get_type_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        if path == 'file/in/source/repo_rev17' and rev == 17:
            return 'file'
        elif path == 'dir/in/source/repo_rev2' and rev == 2:
            return 'dir'
        elif path == 'dir/in/source/repo_rev2/x' and rev == 2:
            return 'file'
        elif path == 'dir/in/source/repo_rev2/y' and rev == 2:
            return 'file'
        else:
            return None

    def get_revision_info(self, rev):
        return RevisionInfoMock()

    def get_uuid(self):
        return 'fake-uuid'

    def get_tree_handle_for_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        if path == 'dir/in/source/repo_rev2' and rev == 2:
            return FakeIterator([
                'dir/in/source/repo_rev2/',
                'dir/in/source/repo_rev2/x',
                'dir/in/source/repo_rev2/y',
            ])
        assert False

        
class TestLumpLumpBuilder(TestCase):

    def setUp(self):
        repo = SvnRepositoryMock()
        self.writer = DumpWriterMock(self)
        self.interesting_paths = InterestingPaths();
        self.builder = LumpBuilder(repo, self.interesting_paths, self.writer);

    def test_delete_lump(self):
        self.builder.delete_path('a/b/c')

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(lump.get_header_keys(), [ 'Node-path', 'Node-action' ])
        self.assertEqual(lump.get_header('Node-path'), 'a/b/c')
        self.assertEqual(lump.get_header('Node-action'), 'delete')

    def test_mkdir(self):
        self.builder.mkdir('a/b/c')

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(lump.get_header_keys(), [ 'Node-path', 'Node-kind', 'Node-action' ])
        self.assertEqual(lump.get_header('Node-path'), 'a/b/c')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')

    def test_add_file_from_source_repo(self):
        self.builder.add_path_from_source_repository('file', 'a/b', 'file/in/source/repo_rev17', 17)
        
        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.get_header('Text-content-length'), '3')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { 'a': 'x1', 'b': 'x2' } )
        self.writer.check_content_tin_of_lump_nr(0, 'xxx')

    def test_add_dir_from_source_repo(self):
        self.builder.add_path_from_source_repository('dir', 'a/b', 'dir/in/source/repo_rev2/', 2)
        
        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { 'a2': 'y1', 'b2': 'y2' } )
        self.writer.check_content_tin_of_lump_nr(0, None)

    def test_clone_change_lump_from_add_lump(self):
        sample_lump = SvnLump()
        sample_lump.set_header('Node-path', 'a/b/c')
        sample_lump.set_header('Node-kind', 'file')
        sample_lump.set_header('Node-action', 'add')
        sample_lump.set_header('Text-content-length', '3')
        sample_lump.set_header('Text-content-md5', 'FAKESUM')
        sample_lump.set_header('Node-copyfrom-path', 'blubber')
        sample_lump.set_header('Node-copyfrom-rev', '2')
        sample_lump.properties =  { 'a': 'x1', 'b': 'x2' }
        sample_fh = StringIO("abcXXX")
        sample_tin = ContentTin(sample_fh, 3, 'FAKESUM')
        sample_lump.content = sample_tin

        self.builder.change_lump_from_add_lump(sample_lump)

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b/c')
        self.assertEqual(lump.get_header('Node-action'), 'change')
        self.assertEqual(lump.get_header('Text-content-length'), '3')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { 'a': 'x1', 'b': 'x2' } )
        self.writer.check_content_tin_of_lump_nr(0, 'abc')

    def test_revision_header(self):
        self.builder.revision_header(23)

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Revision-number' ]
        )
        self.assertEqual(lump.get_header('Revision-number'), '23')
        self.assertEqual(lump.properties, { 'svn:author': 'testuser', 'svn:date': 'some date', 'svn:log': 'log message' })
        self.writer.check_content_tin_of_lump_nr(0, None)

    def test_dump_header_lumps(self):
        self.builder.dump_header_lumps()

        self.assertEqual(len(self.writer.lumps), 2)
        lump = self.writer.lumps[0]
        self.assertEqual(lump.get_header_keys(), [ 'SVN-fs-dump-format-version' ])
        self.assertEqual(lump.get_header('SVN-fs-dump-format-version'), '2')
        self.assertEqual(lump.properties, { })
        self.writer.check_content_tin_of_lump_nr(0, None)

        lump = self.writer.lumps[1]
        self.assertEqual(lump.get_header_keys(), [ 'UUID' ])
        self.assertEqual(lump.get_header('UUID'), 'fake-uuid')
        self.assertEqual(lump.properties, { })
        self.writer.check_content_tin_of_lump_nr(1, None)

    def test_pass_lump(self):
        sample_lump = SvnLump()
        sample_lump.set_header('Marker', 'abc')

        self.builder.pass_lump(sample_lump)

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Marker' ]
        )
        self.assertEqual(lump.get_header('Marker'), 'abc')
        self.assertEqual(lump.properties, { })
        self.writer.check_content_tin_of_lump_nr(0, None)

    def test_add_tree_from_source(self):
        self.interesting_paths.mark_path_as_interesting('a/b')

        self.builder.add_tree_from_source('a/b', 'dir/in/source/repo_rev2/', 2)

        self.assertEqual(len(self.writer.lumps), 3)
        
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { 'a2': 'y1', 'b2': 'y2' } )
        self.writer.check_content_tin_of_lump_nr(0, None)

        lump = self.writer.lumps[1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b/x')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.get_header('Text-content-length'), '1')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(1, 'x')

        lump = self.writer.lumps[2]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b/y')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.get_header('Text-content-length'), '1')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(2, 'y')

    def test_add_tree_from_source_with_boring_path(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.interesting_paths.mark_path_as_boring('a/b/x')

        self.builder.add_tree_from_source('a/b', 'dir/in/source/repo_rev2/', 2)

        self.assertEqual(len(self.writer.lumps), 2)
        
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { 'a2': 'y1', 'b2': 'y2' } )
        self.writer.check_content_tin_of_lump_nr(0, None)

        lump = self.writer.lumps[1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b/y')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.get_header('Text-content-length'), '1')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(1, 'y')
