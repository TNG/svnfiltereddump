
from unittest import TestCase

from LumpBuilderMock import LumpBuilderMock
from RepositoryMock import RepositoryMock

from svnfiltereddump import Config, RevisionIgnorer


class TestRevisionIgnorer(TestCase):
    def setUp(self):
        self.builder = LumpBuilderMock()
        self.ignorer = RevisionIgnorer(self.builder)

    def test_igore_it(self):
        self.ignorer.process_revision(3, None)

        self.assertEqual(len(self.builder.call_history), 1)
        self.assertEqual(self.builder.call_history, [ [ 'revision_header', 3, 'None' ] ])
