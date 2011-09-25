
from unittest import TestCase
from StringIO import StringIO

from svnfiltereddump import SvnLump, LumpBuilder, ContentTin

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
        else:
            assert False

    def get_properties_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        if path == 'file/in/source/repo_rev17' and rev == 17:
            return { 'a': 'x1', 'b': 'x2' }
        elif path == 'dir/in/source/repo_rev2' and rev == 2:
            return { 'a2': 'y1', 'b2': 'y2' }
        else:   
            assert False

    def get_type_of_path(self, path, rev):
        if path[-1:] == '/':
            path = path[:-1]
        if path == 'file/in/source/repo_rev17' and rev == 17:
            return 'file'
        elif path == 'dir/in/source/repo_rev2' and rev == 2:
            return 'dir'
        else:
            return None

    def get_revision_info(self, rev):
        return RevisionInfoMock()

    def get_uuid(self):
        return 'fake-uuid'
        
class SvnLumpTests(TestCase):

    def setUp(self):
        repo = SvnRepositoryMock()
        self.builder = LumpBuilder(repo);

    def test_delete_lump(self):
        lump = self.builder.delete_path('a/b/c')

        self.assertEqual(lump.get_header_keys(), [ 'Node-path', 'Node-action' ])
        self.assertEqual(lump.get_header('Node-path'), 'a/b/c')
        self.assertEqual(lump.get_header('Node-action'), 'delete')

    def test_add_file_from_source_repo(self):
        lump = self.builder.add_path_from_source_repository('file', 'a/b', 'file/in/source/repo_rev17', 17)
        
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
        fh = StringIO()
        lump.content.empty_to(fh)
        fh.seek(0)
        self.assertEqual(fh.read(), 'xxx')

    def test_add_dir_from_source_repo(self):
        lump = self.builder.add_path_from_source_repository('dir', 'a/b', 'dir/in/source/repo_rev2/', 2)
        
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { 'a2': 'y1', 'b2': 'y2' } )

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

        lump = self.builder.change_lump_from_add_lump(sample_lump)

        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b/c')
        self.assertEqual(lump.get_header('Node-action'), 'change')
        self.assertEqual(lump.get_header('Text-content-length'), '3')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { 'a': 'x1', 'b': 'x2' } )
        fh = StringIO()
        lump.content.empty_to(fh)
        fh.seek(0)
        self.assertEqual(fh.read(), 'abc')
        dummy_fh = StringIO()
        self.assertRaises(Exception, sample_lump.content.empty_to, dummy_fh)

    def test_revision_header(self):
        lump = self.builder.revision_header(23)

        self.assertEqual(
            lump.get_header_keys(),
            [ 'Revision-number' ]
        )
        self.assertEqual(lump.get_header('Revision-number'), '23')
        self.assertEqual(lump.properties, { 'svn:author': 'testuser', 'svn:date': 'some date', 'svn:log': 'log message' })
        self.assertEqual(lump.content, None)

    def test_dump_header_lumps(self):
        lumps = self.builder.dump_header_lumps()

        self.assertEqual(len(lumps), 2)

        self.assertEqual(lumps[0].get_header_keys(), [ 'SVN-fs-dump-format-version' ])
        self.assertEqual(lumps[0].get_header('SVN-fs-dump-format-version'), '2')
        self.assertEqual(lumps[0].properties, { })
        self.assertEqual(lumps[0].content, None)

        self.assertEqual(lumps[1].get_header_keys(), [ 'UUID' ])
        self.assertEqual(lumps[1].get_header('UUID'), 'fake-uuid')
        self.assertEqual(lumps[1].properties, { })
        self.assertEqual(lumps[1].content, None)
