from unittest import TestCase

from LumpBuilderMock import LumpBuilderMock

from svnfiltereddump import DumpHeaderGenerator, DUMP_HEADER_PSEUDO_REV


class TestRevisionIgnorer(TestCase):
    def setUp(self):
        self.builder = LumpBuilderMock()
        self.generator = DumpHeaderGenerator(self.builder)

    def test_igore_it(self):
        self.generator.process_revision(DUMP_HEADER_PSEUDO_REV, None)

        self.assertEqual(self.builder.call_history, [['dump_header_lumps']])
