
from unittest import TestCase
from svnfiltereddump import ParentDirectoryLumpGenerator, InterestingPaths

from LumpBuilderMock import LumpBuilderMock

class TestParentDirectoryLumpGenerator(TestCase):
    def setUp(self):
        self.interesting_paths = InterestingPaths()
        self.builder = LumpBuilderMock()
        self.generator = ParentDirectoryLumpGenerator(self.interesting_paths, self.builder)

    def test_empty(self):
        self.generator.write_lumps()
        self.assertEqual(self.builder.call_history, [ ])

    def test_trivial(self):
        self.interesting_paths.mark_path_as_interesting('a')
        self.generator.write_lumps()
        self.assertEqual(self.builder.call_history, [ ])

    def test_all_intersting(self):
        self.interesting_paths.mark_path_as_interesting('')
        self.generator.write_lumps()
        self.assertEqual(self.builder.call_history, [ ])

    def test_simple(self):
        self.interesting_paths.mark_path_as_interesting('a/b')

        self.generator.write_lumps()

        self.assertEqual(self.builder.call_history, [
            [ 'mkdir', 'a' ]
        ])

    def test_complex(self):
        self.interesting_paths.mark_path_as_interesting('a')
        self.interesting_paths.mark_path_as_interesting('b/c')
        self.interesting_paths.mark_path_as_interesting('b/x/y/z1')
        self.interesting_paths.mark_path_as_interesting('b/x/y/z2')
        self.interesting_paths.mark_path_as_interesting('b/x/y/z3')
        self.interesting_paths.mark_path_as_interesting('d/e')

        self.generator.write_lumps()

        self.assertEqual(self.builder.call_history, [
            [ 'mkdir', 'b' ],
            [ 'mkdir', 'd' ],
            [ 'mkdir', 'b/x' ],
            [ 'mkdir', 'b/x/y' ],
        ])
