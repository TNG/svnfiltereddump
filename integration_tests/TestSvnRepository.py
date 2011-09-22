
import unittest
from StringIO import StringIO
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
            env.propset('b/blub', 'prop', 'value2') 
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
            self.repo.get_changed_paths_by_change_type_for_revision(1),
            { 'A': [ 'a/', 'a/bla', 'a/bla2', 'b/', 'b/blub' ] }
        )

    def test_get_changes_rev2(self):
        self.assertEqual(
            self.repo.get_changed_paths_by_change_type_for_revision(2),
            { 'U': [ 'a/bla' ], '_U': [ 'b/blub' ] }
        )

    def test_get_changes_rev3(self):
        self.assertEqual(
            self.repo.get_changed_paths_by_change_type_for_revision(3),
            { 'A': [ 'a/x1', 'a/x2' ], 'D': [ 'a/bla' ] }
        )

    def test_get_tin_for_file(self):
        tin = self.repo.get_tin_for_file('a/bla', 2)
        fh_target = StringIO()
        tin.empty_to(fh_target)
        fh_target.seek(0)
        self.assertEqual(fh_target.read(), 'zzz')

    def test_properties_of_file_empty(self):
        properties = self.repo.get_properties_of_path('b/blub', 1)
        self.assertEqual(properties, { } )

    def test_properties_of_file_multipe(self):
        properties = self.repo.get_properties_of_path('b/blub', 2)
        self.assertEqual(properties, { 'prop': 'value2', 'other_prop': 'other_prop_value' } )

    def test_get_type_of_file(self):
        self.assertEqual(
            self.repo.get_type_of_path('b/blub', 2),
            'file'
        )

    def test_get_type_of_dir(self):
        self.assertEqual(
            self.repo.get_type_of_path('b', 2),
            'dir'
        )

    def test_get_type_of_none_existent_path(self):
        self.assertEqual(
            self.repo.get_type_of_path('b/bogus', 2),
            None
        )
