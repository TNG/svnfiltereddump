
from unittest import TestCase

from LumpBuilderMock import LumpBuilderMock
from RepositoryMock import RepositoryMock

from svnfiltereddump import Config, InterestingPaths, DumpFilter, ContentTin


DUMP_CHANGE_FILE_A_B = """SVN-fs-dump-format-version: 3

UUID: 9fda7f02-01c1-44b6-ae56-f8733c7e9818

Revision-number: 3
Prop-content-length: 105
Content-length: 105

K 7
svn:log
V 3
Bl

K 10
svn:author
V 8
wilhelmh
K 8
svn:date
V 27
2011-09-04T10:27:15.088237Z
PROPS-END

Node-path: a/b
Node-kind: file
Node-action: change
Text-content-length: 2
Text-content-md5: 009520053b00386d1173f3988c55d192
Text-content-sha1: 9063a9f0e032b6239403b719cbbba56ac4e4e45f
Content-length: 2

y


"""

DUMP_COPY_FILE_X_Y_TO_A_B = """SVN-fs-dump-format-version: 3

UUID: 9fda7f02-01c1-44b6-ae56-f8733c7e9818

Revision-number: 3
Prop-content-length: 105
Content-length: 105

K 7
svn:log
V 3
Bl

K 10
svn:author
V 8
wilhelmh
K 8
svn:date
V 27
2011-09-04T10:27:15.088237Z
PROPS-END

Node-path: a/b
Node-kind: file
Node-action: add
Node-copyfrom-rev: 2
Node-copyfrom-path: x/y
Text-copy-source-md5: 20f3637543da7cda2f6a984fdbedfeb2
Text-copy-source-sha1: 24d212ee2d9b2655ab5e803dd8eac4b34f703f24

"""

DUMP_COPY_FILE_X_Y_TO_A_B_WITH_CHANGE = """SVN-fs-dump-format-version: 3

UUID: 9fda7f02-01c1-44b6-ae56-f8733c7e9818

Revision-number: 3
Prop-content-length: 105
Content-length: 105

K 7
svn:log
V 3
Bl

K 10
svn:author
V 8
wilhelmh
K 8
svn:date
V 27
2011-09-04T10:27:15.088237Z
PROPS-END

Node-path: a/b
Node-kind: file
Node-action: add
Node-copyfrom-rev: 2
Node-copyfrom-path: x/y
Text-copy-source-md5: 20f3637543da7cda2f6a984fdbedfeb2
Text-copy-source-sha1: 24d212ee2d9b2655ab5e803dd8eac4b34f703f24
Text-content-length: 2
Text-content-md5: 009520053b00386d1173f3988c55d192
Text-content-sha1: 9063a9f0e032b6239403b719cbbba56ac4e4e45f
Prop-content-length: 52
Content-length: 52

K 5
propa
V 6
value2
K 5
propb
V 6
valueb
PROPS-END
y


"""

DUMP_COPY_DIR_X_Y_TO_A_B = """SVN-fs-dump-format-version: 3

UUID: 9fda7f02-01c1-44b6-ae56-f8733c7e9818

Revision-number: 3
Prop-content-length: 105
Content-length: 105

K 7
svn:log
V 3
Bl

K 10
svn:author
V 8
wilhelmh
K 8
svn:date
V 27
2011-09-04T10:27:15.088237Z
PROPS-END

Node-path: a/b
Node-kind: dir
Node-action: add
Node-copyfrom-rev: 2
Node-copyfrom-path: x/y

"""


DUMP_DELETE_FILE_A_B = """SVN-fs-dump-format-version: 3

UUID: 9fda7f02-01c1-44b6-ae56-f8733c7e9818

Revision-number: 3
Prop-content-length: 105
Content-length: 105

K 7
svn:log
V 3
Bl

K 10
svn:author
V 8
wilhelmh
K 8
svn:date
V 27
2011-09-04T10:27:15.088237Z
PROPS-END

Node-path: a/b
Node-action: delete

"""



class TestDumpFilter(TestCase):
    def setUp(self):
        self.config = Config([ '/dummy' ])
        self.interesting_paths = InterestingPaths()
        self.repo = RepositoryMock()
        self.builder = LumpBuilderMock()
        self.dump_filter = DumpFilter(
            config = self.config,
            source_repository = self.repo,
            interesting_paths = self.interesting_paths,
            lump_builder = self.builder
        )

    def test_dump_empty(self):
        self.interesting_paths.mark_path_as_interesting('other/path')
        self.repo.dumps_by_revision[3] = DUMP_CHANGE_FILE_A_B

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 1)
        self._verfiy_revision_header()

    def test_dump_simple(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.repo.dumps_by_revision[3] = DUMP_CHANGE_FILE_A_B

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 2)

        self._verfiy_revision_header()

        self.assertEqual(self.builder.call_history[1][0], 'pass_lump' )
        lump = self.builder.call_history[1][1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Text-content-length',
            'Text-content-md5', 'Text-content-sha1', 'Content-length' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'change')
        self._assertTin(lump, "y\n")

    def test_internal_copy(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.interesting_paths.mark_path_as_interesting('x/y')
        self.repo.dumps_by_revision[3] = DUMP_COPY_FILE_X_Y_TO_A_B

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 2)
        self._verfiy_revision_header()

        self.assertEqual(self.builder.call_history[1][0], 'pass_lump' )
        lump = self.builder.call_history[1][1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Node-copyfrom-rev',
            'Node-copyfrom-path', 'Text-copy-source-md5', 'Text-copy-source-sha1' ]
        )
        self.assertEqual(lump.properties, { })
        self.assertEqual(lump.content, None)

    def test_copy_in(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.repo.dumps_by_revision[3] = DUMP_COPY_FILE_X_Y_TO_A_B
        self.repo.files_by_name_and_revision['x/y'] = { 2: "xxx\n\yyy\n" }
        self.repo.properties_path_and_revision['x/y'] = { 2: { } }

        self.dump_filter.process_revision(3)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1],
            [ 'add_path_from_source_repository', 'file', 'a/b', 'x/y', 2 ]
        )

    def test_copy_in_start_rev(self):
        self.config.start_rev = 3
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.interesting_paths.mark_path_as_interesting('x/y')
        self.repo.dumps_by_revision[3] = DUMP_COPY_FILE_X_Y_TO_A_B
        self.repo.files_by_name_and_revision['x/y'] = { 2: "xxx\n\yyy\n" }
        self.repo.properties_path_and_revision['x/y'] = { 2: { } }

        self.dump_filter.process_revision(3)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1],
            [ 'add_path_from_source_repository', 'file', 'a/b', 'x/y', 2 ]
        )

    def test_copy_in_with_change(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.repo.dumps_by_revision[3] = DUMP_COPY_FILE_X_Y_TO_A_B_WITH_CHANGE
        self.repo.files_by_name_and_revision['x/y'] = { 2: "xxx\n\yyy\n" }
        self.repo.properties_path_and_revision['x/y'] = { 2: { 'prop1': 'value1' } }

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 3)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1], 
            [ 'add_path_from_source_repository', 'file', 'a/b', 'x/y', 2 ]
        )

        self.assertEqual(self.builder.call_history[2][0], 'change_lump_from_add_lump')
        lump = self.builder.call_history[2][1]
        self.assertEqual(
            lump.get_header_keys(),
            ['Node-path', 'Node-kind', 'Node-action', 'Node-copyfrom-rev', 'Node-copyfrom-path',
            'Text-copy-source-md5', 'Text-copy-source-sha1', 'Text-content-length', 'Text-content-md5',
            'Text-content-sha1', 'Prop-content-length', 'Content-length']
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { 'propa': 'value2', 'propb': 'valueb' } )
        self._assertTin(lump, "y\n")

    def test_copy_in_dir(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.repo.dumps_by_revision[3] = DUMP_COPY_DIR_X_Y_TO_A_B 
        self.repo.tree_by_path_and_revision['x/y'] = { 2: [ 'x/y/', 'x/y/c1', 'x/y/c2' ] }
        self.repo.files_by_name_and_revision['x/y/c1'] = { 2: "xxx\n\yy1\n" }
        self.repo.files_by_name_and_revision['x/y/c2'] = { 2: "xxx\n\yy2\n" }
        self.repo.properties_path_and_revision['x/y'] = { 2: { 'prop1': 'value1' } }
        self.repo.properties_path_and_revision['x/y/c1'] = { 2: { 'prop2': 'value2' } }
        self.repo.properties_path_and_revision['x/y/c2'] = { 2: { } }

        self.dump_filter.process_revision(3)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1],
            [ 'add_tree_from_source', 'a/b', 'x/y', 2 ]
        )
        
    def test_delete_inside(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.repo.dumps_by_revision[3] = DUMP_DELETE_FILE_A_B

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 2)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1][0], 'pass_lump')

        lump = self.builder.call_history[1][1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'a/b')
        self.assertEqual(lump.get_header('Node-action'), 'delete')
        self.assertEqual(lump.properties, { })
        self.assertEqual(lump.content, None)

    def test_delete_over_existing(self):
        self.interesting_paths.mark_path_as_interesting('a/b/c')
        self.repo.dumps_by_revision[3] = DUMP_DELETE_FILE_A_B
        self.repo.files_by_name_and_revision['a/b/c'] = { 2: "xxx\n\yyy\n" }

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 2)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1], 
            [ 'delete_path', 'a/b/c' ]
        )

    def test_delete_over_non_existing(self):
        self.interesting_paths.mark_path_as_interesting('a/b/c')
        self.repo.dumps_by_revision[3] = DUMP_DELETE_FILE_A_B

        self.dump_filter.process_revision(3)

        self.assertEqual(len(self.builder.call_history), 1)
        self._verfiy_revision_header()

    def _verfiy_revision_header(self):
        self.assertEqual(self.builder.call_history[0][0], 'pass_lump')
        lump = self.builder.call_history[0][1]
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Revision-number', 'Prop-content-length', 'Content-length' ]
        )
        self.assertEqual(lump.get_header('Revision-number'), '3')
        self.assertEqual(
            lump.properties,
            { 'svn:log': "Bl\n", 'svn:author': 'wilhelmh', 'svn:date': '2011-09-04T10:27:15.088237Z' }
        )

    def _assertTin(self, lump, expected_content):
        # Hack: Works only in conjunction with LumpBuilderMock
        self.assertEqual(lump.content, expected_content)
 
