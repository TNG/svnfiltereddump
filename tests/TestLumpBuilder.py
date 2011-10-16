
from unittest import TestCase
from StringIO import StringIO

from svnfiltereddump import Config, SvnLump, LumpBuilder, ContentTin, InterestingPaths

from DumpWriterMock import DumpWriterMock
from RepositoryMock import RepositoryMock


class TestLumpBuilder(TestCase):

    def setUp(self):
        self.config = Config(['/repo'])
        self.repo = RepositoryMock()
        self.writer = DumpWriterMock(self)
        self.interesting_paths = InterestingPaths();
        self.builder = LumpBuilder(self.config, self.repo, self.interesting_paths, self.writer);

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
        self.repo.files_by_name_and_revision['file/in/source/repo_rev17'] = { 17: 'xxx' }
        self.repo.properties_by_path_and_revision['file/in/source/repo_rev17'] = { 17:  { 'a': 'x1', 'b': 'x2' } }
        
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
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKEMD5')
        self.assertEqual(lump.properties, { 'a': 'x1', 'b': 'x2' } )
        self.writer.check_content_tin_of_lump_nr(0, 'xxx')

    def test_add_dir_from_source_repo(self):
        self.repo.tree_by_path_and_revision['dir/in/source/repo_rev2'] = { 2: [ 'dir/in/source/repo_rev2/' ] }
        self.repo.properties_by_path_and_revision['dir/in/source/repo_rev2'] = { 2:  { 'a2': 'y1', 'b2': 'y2' } }

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

    def test_add_path_from_target(self):
        self.builder.add_path_from_target('new/path', 'file', 'source/path', 17)

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Node-copyfrom-path', 'Node-copyfrom-rev' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'new/path')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.get_header('Node-copyfrom-path'), 'source/path')
        self.assertEqual(lump.get_header('Node-copyfrom-rev'), '17')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(0, None)

    def test_clone_change_lump_from_add_lump(self):
        sample_lump = SvnLump()
        sample_lump.set_header('Node-path', 'a/b/c')
        sample_lump.set_header('Node-kind', 'file')
        sample_lump.set_header('Node-action', 'add')
        sample_lump.set_header('Text-content-length', '3')
        sample_lump.set_header('Text-content-md5', 'FAKEMD5')
        sample_lump.set_header('Node-copyfrom-path', 'blubber')
        sample_lump.set_header('Node-copyfrom-rev', '2')
        sample_lump.properties =  { 'a': 'x1', 'b': 'x2' }
        sample_fh = StringIO("abcXXX")
        sample_tin = ContentTin(sample_fh, 3, 'FAKEMD5')
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
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKEMD5')
        self.assertEqual(lump.properties, { 'a': 'x1', 'b': 'x2' } )
        self.writer.check_content_tin_of_lump_nr(0, 'abc')

    def test_revision_header(self):
        self.repo.revision_properties_by_revision[23] = [ 'testuser', 'some date', 'log message' ]
        
        self.builder.revision_header(23, 'my title')

        self.assertEqual(len(self.writer.lumps), 1)
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Revision-number' ]
        )
        self.assertEqual(lump.get_header('Revision-number'), '23')
        self.assertEqual(lump.properties, { 'svn:author': 'testuser', 'svn:date': 'some date', 'svn:log': 'my title' })
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
        self.repo.tree_by_path_and_revision['source/dir'] = { 2: [ 'source/dir/', 'source/dir/x', 'source/dir/y' ] }
        self.repo.properties_by_path_and_revision['source/dir'] = { 2: { 'a2': 'y1', 'b2': 'y2' } }
        self.repo.files_by_name_and_revision['source/dir/x'] = { 2: 'x' }
        self.repo.properties_by_path_and_revision['source/dir/x'] = { 2: { } }
        self.repo.files_by_name_and_revision['source/dir/y'] = { 2: 'y' }
        self.repo.properties_by_path_and_revision['source/dir/y'] = { 2: { } }
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.builder.add_tree_from_source('a/b', 'source/dir', 2)

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
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKEMD5')
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
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKEMD5')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(2, 'y')

    def test_add_tree_from_source_with_boring_path(self):
        self.repo.tree_by_path_and_revision['source/dir'] = { 2: [ 'source/dir/', 'source/dir/x', 'source/dir/y' ] }
        self.repo.properties_by_path_and_revision['source/dir'] = { 2: { 'a2': 'y1', 'b2': 'y2' } }
        self.repo.files_by_name_and_revision['source/dir/x'] = { 2: 'x' }
        self.repo.properties_by_path_and_revision['source/dir/x'] = { 2: { } }
        self.repo.files_by_name_and_revision['source/dir/y'] = { 2: 'y' }
        self.repo.properties_by_path_and_revision['source/dir/y'] = { 2: { } }
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.interesting_paths.mark_path_as_boring('a/b/x')

        self.builder.add_tree_from_source('a/b', 'source/dir/', 2)

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
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKEMD5')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(1, 'y')

    def test_add_tree_from_source_with_current_tag(self):
        self.repo.tree_by_path_and_revision['source/dir'] = { 5: [ 'source/dir/', 'source/dir/x' ] }
        self.repo.properties_by_path_and_revision['source/dir'] = { 5: { 'a2': 'y1', 'b2': 'y2' } }
        self.repo.files_by_name_and_revision['source/dir/x'] = { 5: 'x' }
        self.repo.properties_by_path_and_revision['source/dir/x'] = { 5: { } }
        self.config.start_rev = 4
        self.config.drop_old_tags_and_branches = True
        self.interesting_paths.mark_path_as_interesting('a')

        self.builder.add_tree_from_source('a/tags/NEW_TAG', 'source/dir/', 5)

        self.assertEqual(len(self.writer.lumps), 0)
        self.assertFalse(self.interesting_paths.is_interesting('a/tags/NEW_TAG'))

    def test_add_tree_from_source_with_obsolte_tag(self):
        self.repo.tree_by_path_and_revision['source/dir'] = { 5: [ 'source/dir/', 'source/dir/x' ] }
        self.repo.properties_by_path_and_revision['source/dir'] = { 5: { 'a2': 'y1', 'b2': 'y2' } }
        self.repo.files_by_name_and_revision['source/dir/x'] = { 5: 'x' }
        self.repo.properties_by_path_and_revision['source/dir/x'] = { 5: { } }
        self.config.start_rev = 6
        self.config.drop_old_tags_and_branches = True
        self.interesting_paths.mark_path_as_interesting('a')

        self.builder.add_tree_from_source('a/tags/OLD_TAG', 'source/dir/', 5)

        self.assertEqual(len(self.writer.lumps), 0)
        self.assertFalse(self.interesting_paths.is_interesting('a/tags/OLD_TAG'))

    def test_add_tree_from_source_with_valid_tag_inside(self):
        self.repo.tree_by_path_and_revision['source/dir'] = { 5: [
            'source/dir/', 'source/dir/tags/', 'source/dir/tags/NEW_TAG/', 'source/dir/tags/NEW_TAG/x'
        ] }
        self.repo.properties_by_path_and_revision['source/dir'] = { 5: { } }
        self.repo.tree_by_path_and_revision['source/dir/tags'] = { 5: [
            'source/dir/tags/', 'source/dir/tags/NEW_TAG/', 'source/dir/tags/NEW_TAG/x'
        ] }
        self.repo.properties_by_path_and_revision['source/dir/tags'] = { 5: { } }
        self.repo.tree_by_path_and_revision['source/dir/tags/NEW_TAG'] = { 5: [
            'source/dir/tags/NEW_TAG/', 'source/dir/tags/NEW_TAG/x'
        ] }
        self.repo.properties_by_path_and_revision['source/dir/tags/NEW_TAG'] = { 5: { } }
        self.repo.files_by_name_and_revision['source/dir/tags/NEW_TAG/x'] = { 5: 'x' }
        self.repo.properties_by_path_and_revision['source/dir/tags/NEW_TAG/x'] = { 5: { } }
        self.config.start_rev = 3
        self.config.drop_old_tags_and_branches = True
        self.interesting_paths.mark_path_as_interesting('a')

        self.builder.add_tree_from_source('a', 'source/dir/', 5)
        
        self.assertEqual(len(self.writer.lumps), 2)
        self.assertFalse(self.interesting_paths.is_interesting('a/tags/NEW_TAG'))

        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(0, None)

        lump = self.writer.lumps[1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/tags')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(1, None)

    def test_add_tree_from_source_with_obsolete_tag_inside(self):
        self.repo.tree_by_path_and_revision['source/dir'] = { 5: [
            'source/dir/', 'source/dir/tags/', 'source/dir/tags/OLD_TAG', 'source/dir/tags/OLD_TAG/x'
         ] }
        self.repo.properties_by_path_and_revision['source/dir'] = { 5: { } }
        self.repo.tree_by_path_and_revision['source/dir/tags'] = { 5: [
            'source/dir/tags/', 'source/dir/tags/OLD_TAG/', 'source/dir/tags/OLD_TAG/x'
        ] }
        self.repo.properties_by_path_and_revision['source/dir/tags'] = { 5: { } }
        self.repo.tree_by_path_and_revision['source/dir/tags/OLD_TAG'] = { 5: [
            'source/dir/tags/OLD_TAG', 'source/dir/tags/OLD_TAG/x'
        ] }
        self.repo.properties_by_path_and_revision['source/dir/tags/OLD_TAG'] = { 5: { } }
        self.repo.files_by_name_and_revision['source/dir/tags/OLD_TAG/x'] = { 5: 'x' }
        self.repo.properties_by_path_and_revision['source/dir/tags/OLD_TAG/x'] = { 5: { } }
        self.config.start_rev = 7
        self.config.drop_old_tags_and_branches = True
        self.interesting_paths.mark_path_as_interesting('a')

        self.builder.add_tree_from_source('a', 'source/dir/', 5)

        self.assertEqual(len(self.writer.lumps), 2)
        self.assertFalse(self.interesting_paths.is_interesting('a/tags/OLD_TAG'))
        
        lump = self.writer.lumps[0]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(0, None)

        lump = self.writer.lumps[1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/tags')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { } )
        self.writer.check_content_tin_of_lump_nr(1, None)

