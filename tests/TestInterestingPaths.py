
from unittest import TestCase

from svnfiltereddump import InterestingPaths

class InterestingPathsTests(TestCase):

    def test_empty_string(self):
        interesting_path = InterestingPaths()
        interesting_path.mark_path_as_interesting('')

        self.assertTrue(interesting_path.is_interesting('a'))
        self.assertTrue(interesting_path.is_interesting('b'))

        dirs = sorted(interesting_path.get_interesting_sub_directories('a'))
        self.assertEqual(dirs, [ 'a' ])

        dirs = sorted(interesting_path.get_interesting_sub_directories(''))
        self.assertEqual(dirs, [ '' ])

    def test_simple_include(self):
        interesting_path = InterestingPaths()
        interesting_path.mark_path_as_interesting('a/b/c')

        self.assertTrue(interesting_path.is_interesting('a/b/c'))
        self.assertTrue(interesting_path.is_interesting('a/b/c/d'))
        self.assertFalse(interesting_path.is_interesting('a/b'))
        self.assertFalse(interesting_path.is_interesting('x/y'))

    def test_include_with_exclude(self):
        interesting_path = InterestingPaths()
        interesting_path.mark_path_as_interesting('a/b/c')
        interesting_path.mark_path_as_boring('a/b/c/x')

        self.assertTrue(interesting_path.is_interesting('a/b/c'))
        self.assertTrue(interesting_path.is_interesting('a/b/c/d'))
        self.assertFalse(interesting_path.is_interesting('a/b'))
        self.assertFalse(interesting_path.is_interesting('x/y'))
        self.assertFalse(interesting_path.is_interesting('a/b/c/x'))
        self.assertFalse(interesting_path.is_interesting('a/b/c/x/y'))

    def test_get_interesting_sub_directories(self):
        interesting_path = InterestingPaths()
        interesting_path.mark_path_as_interesting('a/b/ca')
        interesting_path.mark_path_as_interesting('a/b/cb')
        interesting_path.mark_path_as_boring('a/b/ca/x')
        interesting_path.mark_path_as_boring('a/y')
        
        dirs = sorted(interesting_path.get_interesting_sub_directories('a/b'))
        self.assertEqual(dirs, [ 'a/b/ca', 'a/b/cb' ])

        self.assertEqual([], interesting_path.get_interesting_sub_directories("a/b/c/x"))
