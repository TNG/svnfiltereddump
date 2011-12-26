
from unittest import TestCase

from LumpBuilderMock import LumpBuilderMock
from RepositoryMock import RepositoryMock

from svnfiltereddump import Config, InterestingPaths, BootsTrapper

class TestBootsTrapper(TestCase):
    def setUp(self):
        self.config = Config([ '/dummy' ])
        self.interesting_paths = InterestingPaths()
        self.repo = RepositoryMock()
        self.repo.revision_properties_by_revision[3] = [ 'some author', 'some date', 'same log message' ]
        self.builder = LumpBuilderMock()
        self.boots_trapper = BootsTrapper(
            config = self.config,
            source_repository = self.repo,
            interesting_paths = self.interesting_paths,
            lump_builder = self.builder
        )

    def test_empty(self):
        self.boots_trapper.process_revision(3, None)
        self._verfiy_revision_header()

    def test_simple_file(self):
        self.interesting_paths.mark_path_as_interesting('a/b')
        self.repo.tree_by_path_and_revision['a/b'] = { 3: [ 'a/b' ] }
        self.repo.files_by_name_and_revision['a/b'] = { 3: "xxx\n\yyy\n" }

        self.boots_trapper.process_revision(3, None)

        self.assertEqual(len(self.builder.call_history), 2)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1], [ 'get_recursively_from_source', 'file', 'a/b', 'add', 'a/b', 3 ])

    def test_simple_dir(self):
        self.interesting_paths.mark_path_as_interesting('a/b/c')
        self.repo.tree_by_path_and_revision['a/b/c'] = { 3: [ 'a/b/c/', 'a/b/c/x', 'a/b/c/y' ] }
        self.repo.files_by_name_and_revision['a/b/c/x'] = { 3: "xxx" }
        self.repo.files_by_name_and_revision['a/b/c/y'] = { 3: "yyy" }

        self.boots_trapper.process_revision(3, None)

        self.assertEqual(len(self.builder.call_history), 2)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1], [ 'get_recursively_from_source', 'dir', 'a/b/c', 'add', 'a/b/c', 3 ])

    def test_multi_dir(self):
        self.interesting_paths.mark_path_as_interesting('a/a')
        self.interesting_paths.mark_path_as_interesting('a/b/x')
        self.interesting_paths.mark_path_as_interesting('a/b/y')
        self.interesting_paths.mark_path_as_interesting('a/b/z')
        self.repo.tree_by_path_and_revision['a/a'] = { 3: [ 'a/a/', 'a/a/a' ] }
        self.repo.files_by_name_and_revision['a/a/a'] = { 3: "A" }
        self.repo.tree_by_path_and_revision['a/b/x'] = { 3: [ 'a/b/c/', 'a/b/c/x', 'a/b/c/y' ] }
        self.repo.files_by_name_and_revision['a/b/x/x1'] = { 3: "111" }
        self.repo.files_by_name_and_revision['a/b/x/x2'] = { 3: "222" }
        self.repo.files_by_name_and_revision['a/b/y'] = { 3: "yyy" }

        self.boots_trapper.process_revision(3, None)

        self.assertEqual(len(self.builder.call_history), 4)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1], [ 'get_recursively_from_source', 'dir', 'a/a', 'add', 'a/a', 3 ])
        self.assertEqual(self.builder.call_history[2], [ 'get_recursively_from_source', 'dir', 'a/b/x', 'add', 'a/b/x', 3 ])
        self.assertEqual(self.builder.call_history[3], [ 'get_recursively_from_source', 'file', 'a/b/y', 'add', 'a/b/y', 3 ])

    def _verfiy_revision_header(self):
        self.assertEqual(self.builder.call_history[0], [ 'revision_header', 3, 'svnfiltereddump boots trap revision' ])

