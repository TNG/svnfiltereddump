
import unittest
from svn_repo_test_environment import TestEnvironment

from svnfiltereddump import SvnRepository

env = None

class TestSvnRepository(unittest.TestCase):

    def setUp(self):
        global env
        if env is None:
            env = TestEnvironment()
            # Revision 1
            env.mkdir('a')
            env.add_file('a/bla', 'xxx')
            env.propset('a/bla', 'some_prop', 'prop_value') 
            env.add_file('a/bla2', 'aaa')
            env.mkdir('b')
            env.add_file('b/blub', 'yyy')
            env.commit('c1')
            # Revision 2
            env.change_file('a/bla', 'zzz')
            env.propset('b/blub', 'other_prop', 'other_prop_value') 
            env.commit('c2')
            # Revision 3
            env.add_file('a/x1', 'x11111')
            env.add_file('a/x2', 'x22222')
            env.rm_file('a/bla')
            env.commit('c3')
        self.env = env
        self.repo = SvnRepository(env.repo_path)

    def test_get_changes_rev1(self):
        self.assertEqual(
            self.repo.get_changed_paths_by_change_type(1),
            { 'A': [ 'a/', 'a/bla', 'a/bla2', 'b/', 'b/blub' ] }
        )

    def test_get_changes_rev2(self):
        self.assertEqual(
            self.repo.get_changed_paths_by_change_type(2),
            { 'U': [ 'a/bla' ], '_U': [ 'b/blub' ] }
        )

    def test_get_changes_rev3(self):
        self.assertEqual(
            self.repo.get_changed_paths_by_change_type(3),
            { 'A': [ 'a/x1', 'a/x2' ], 'D': [ 'a/bla' ] }
        )
        
