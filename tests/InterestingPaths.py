
from unittest import TestCase

from svnfiltereddump import InterestingPaths

class InterestingPathsTests(TestCase):

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

    
