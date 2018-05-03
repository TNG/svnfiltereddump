from unittest import TestCase

from LumpBuilderMock import LumpBuilderMock
from RepositoryMock import RepositoryMock

from svnfiltereddump import SyntheticDeleter


class TestSyntheticDeleter(TestCase):
    def setUp(self):
        self.repo = RepositoryMock()
        self.repo.revision_properties_by_revision[3] = ['some author', 'some date', 'same log message']
        self.builder = LumpBuilderMock()
        self.deleter = SyntheticDeleter(
            source_repository=self.repo,
            lump_builder=self.builder
        )

    def test_no_delete(self):
        self.deleter.process_revision(3, ['a/b'])

        self.assertEqual(len(self.builder.call_history), 1)
        self._verfiy_revision_header()

    def test_delete_simple(self):
        self.repo.tree_by_path_and_revision['a/b'] = {2: ['a/b/']}

        self.deleter.process_revision(3, ['a/b'])

        self.assertEqual(len(self.builder.call_history), 2)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1],
                         ['delete_path', 'a/b']
                         )

    def test_delete_complex(self):
        self.repo.tree_by_path_and_revision['a/b'] = {2: ['a/b/']}
        self.repo.tree_by_path_and_revision['x/y'] = {2: ['x/y/', 'x/y/bla', 'x/y/z', 'x/y/z/blub']}
        self.repo.tree_by_path_and_revision['x/y/z'] = {2: ['x/y/z', 'x/y/z/blub']}
        self.repo.files_by_name_and_revision['x/y/bla'] = {2: "bbblllaaa\n"}
        self.repo.files_by_name_and_revision['x/y/z/blub'] = {2: "bluuub\n"}

        self.deleter.process_revision(3, ['g/h', 'a/b', 'x/y/z', 'x/y/bla', 'x/y/bla2'])

        self.assertEqual(len(self.builder.call_history), 4)
        self._verfiy_revision_header()
        self.assertEqual(self.builder.call_history[1:], [
            ['delete_path', 'a/b'],
            ['delete_path', 'x/y/z'],
            ['delete_path', 'x/y/bla'],
        ])

    def _verfiy_revision_header(self):
        self.assertEqual(self.builder.call_history[0], ['revision_header', 3, 'None'])
