
import unittest
from subprocess import call

from functional_test_environment import TestEnvironment

class ComandLineFeatureTests(unittest.TestCase):
    
    def setUp(self):
        self.env = TestEnvironment()

    def tearDown(self):
        self.env.destroy()

    def test_basic_call(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.propset('a/bla', 'some_prop', 'prop_value')
        env.mkdir('b')
        env.add_file('b/blub', 'yyy')
        env.commit('c1')
        # Revision 2
        env.change_file('a/bla', 'zzz')
        env.commit('c2')

        env.filter_repo( [ 'a' ] )

        self.assertTrue(env.is_existing_in_rev('a', 1), 'Dir a was copied in rev 1')
        self.assertFalse(env.is_existing_in_rev('b', 1), 'Dir b was not copied in rev 1')
        self.assertEquals(env.get_file_contens_in_rev('a/bla', 1), 'xxx', 'File a/bla correct in rev 1')
        self.assertEquals(env.get_file_contens_in_rev('a/bla', 2), 'zzz', 'File a/bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('a/bla', 2, 'some_prop'), 'prop_value', 'File a/bla property correct in rev 2')
        self.assertEquals(env.get_log_of_file_in_rev('a/bla', 2), [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_include(self):
        env = self.env
        env.mkdir('x/a')
        env.mkdir('x/b')
        env.add_file('x/a/bla', 'xxx')
        env.add_file('x/b/blub', 'yyy')
        env.add_file('x/foo', 'zzz')
        env.add_file('x/bar', 'ZZZ')
        env.commit('c1')

        env.mkdir_target('x') # Rev 1 in target

        env.filter_repo( [ 'x/a', 'x/foo' ] ) 

        self.assertTrue(env.is_existing_in_rev('x/a/bla', 2), 'File bla was copied')
        self.assertTrue(env.is_existing_in_rev('x/foo', 2), 'File foo was copied')
        self.assertFalse(env.is_existing_in_rev('x/b/blub', 2), 'File blub was NOT copied')
        self.assertFalse(env.is_existing_in_rev('x/bar', 2), 'File bar was NOT copied')

    def test_include_file(self):
        env = self.env
        env.mkdir('x/a')
        env.mkdir('x/b')
        env.add_file('x/a/bla', 'xxx')
        env.add_file('x/b/blub', 'yyy')
        env.add_file('x/foo', 'zzz')
        env.add_file('x/bar', 'ZZZ')
        env.commit('c1')

        env.mkdir_target('x') # Rev 1 in target
        include_file = env.create_tmp_file("x/a\n" + "x/foo\n")

        env.filter_repo( [ '--include-file', include_file ] ) 

        self.assertTrue(env.is_existing_in_rev('x/a/bla', 2), 'File bla was copied')
        self.assertTrue(env.is_existing_in_rev('x/foo', 2), 'File foo was copied')
        self.assertFalse(env.is_existing_in_rev('x/b/blub', 2), 'File blub was NOT copied')
        self.assertFalse(env.is_existing_in_rev('x/bar', 2), 'File bar was NOT copied')

    def test_exclude(self):
        env = self.env
        env.mkdir('x/a')
        env.mkdir('x/b')
        env.add_file('x/a/bla', 'xxx')
        env.add_file('x/b/blub', 'yyy')
        env.add_file('x/foo', 'zzz')
        env.add_file('x/bar', 'ZZZ')
        env.commit('c1')

        env.filter_repo( [ 'x', '--exclude', 'x/b', '--exclude', 'x/bar' ] ) 

        self.assertTrue(env.is_existing_in_rev('x/a/bla', 1), 'File bla was copied')
        self.assertTrue(env.is_existing_in_rev('x/foo', 1), 'File foo was copied')
        self.assertFalse(env.is_existing_in_rev('x/b/blub', 1), 'File blub was NOT copied')
        self.assertFalse(env.is_existing_in_rev('x/bar', 1), 'File bar was NOT copied')

    def test_exclude_file(self):
        env = self.env
        env.mkdir('x/a')
        env.mkdir('x/b')
        env.add_file('x/a/bla', 'xxx')
        env.add_file('x/b/blub', 'yyy')
        env.add_file('x/foo', 'zzz')
        env.add_file('x/bar', 'ZZZ')
        env.commit('c1')

        exclude_file = env.create_tmp_file("x/b\n" + "x/bar\n")

        env.filter_repo( [ 'x', '--exclude-file', exclude_file ] ) 

        self.assertTrue(env.is_existing_in_rev('x/a/bla', 1), 'File bla was copied')
        self.assertTrue(env.is_existing_in_rev('x/foo', 1), 'File foo was copied')
        self.assertFalse(env.is_existing_in_rev('x/b/blub', 1), 'File blub was NOT copied')
        self.assertFalse(env.is_existing_in_rev('x/bar', 1), 'File bar was NOT copied')

    def test_dont_drop_empty_revs(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.mkdir('b')
        env.commit('c2')
        # Revision 3
        env.change_file('a/bla', 'yyy')
        env.commit('c3')

        env.filter_repo( [ 'a' ] )

        self.assertEquals(env.get_log_of_file_in_rev('a/bla', 3), [ [ 3, 'c3' ], [ 1, 'c1' ] ])
        self.assertEquals(env.get_log_of_revision(2), 'c2')
         
    def test_drop_empty_revs(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.mkdir('b')
        env.commit('c2')
        # Revision 3
        env.change_file('a/bla', 'yyy')
        env.commit('c3')

        env.filter_repo( [ '--drop-empty-revs', 'a' ] )

        self.assertEquals(env.get_log_of_file_in_rev('a/bla', 3), [ [ 3, 'c3' ], [ 1, 'c1' ] ])
        self.assertEquals(env.get_log_of_revision(2), '') # Don't know yet what the behavior will be

    def test_renumber_revs(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.mkdir('b')
        env.commit('c2')
        # Revision 3
        env.change_file('a/bla', 'yyy')
        env.commit('c3')

        env.filter_repo( [ '--drop-empty-revs', '--renumber-revs', 'a' ] )

        self.assertEquals(env.get_log_of_file_in_rev('a/bla', 2), [ [ 2, 'c3' ], [ 1, 'c1' ] ])

    def test_start_rev(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.change_file('b/bla', 'yyy')
        env.commit('c2')

        env.filter_repo( [ '--start-rev', '2', 'a' ] )

        self.assertEquals(env.get_file_contens_in_rev('a/bla', 2), 'yyy', 'File a/bla correct in rev 2')
        self.assertEquals(env.get_log_of_file_in_rev('a/bla', 2), [ [ 2, 'c2' ] ])

        
if __name__ == '__main__':
    unittest.main()
