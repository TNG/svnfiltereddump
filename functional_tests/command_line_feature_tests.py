
import unittest
from subprocess import call

from functional_test_environment import TestEnvironment


class ComandLineFeatureTests(unittest.TestCase):
    
    def setUp(self):
        self.env = TestEnvironment()

    def tearDown(self):
        self.env.destroy()

    def filter_repo_and_check(self, params):
        error = self.env.filter_repo(params)
        if error is not None:
            self.fail("Filter failed: " + error)

    def check_log_of_file_in_rev(self, name, rev, exected_log):
        ( parsed_log, error ) = self.env.get_log_of_file_in_rev(name, rev)
        if error is None:
            self.assertEquals(parsed_log, exected_log)
        else:
            self.fail(
                "Failed to get log of file %s in revision %d with error:\n%s"
                %  ( name, rev, error )
            )

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

        self.filter_repo_and_check( [ 'a' ] )

        self.assertTrue(env.is_existing_in_rev('a', 1), 'Dir a was copied in rev 1')
        self.assertFalse(env.is_existing_in_rev('b', 1), 'Dir b was not copied in rev 1')
        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'xxx', 'File a/bla correct in rev 1')
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'zzz', 'File a/bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('a/bla', 2, 'some_prop'), 'prop_value', 'File a/bla property correct in rev 2')
        self.check_log_of_file_in_rev('a/bla', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

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

        self.filter_repo_and_check( [ 'x/a', 'x/foo' ] ) 

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

        self.filter_repo_and_check( [ '--include-file', include_file ] ) 

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

        self.filter_repo_and_check( [ 'x', '--exclude', 'x/b', '--exclude', 'x/bar' ] ) 

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

        self.filter_repo_and_check( [ 'x', '--exclude-file', exclude_file ] ) 

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

        self.filter_repo_and_check( [ 'a', '--keep-empty-revs' ] )

        self.check_log_of_file_in_rev('a/bla', 3, [ [ 3, 'c3' ], [ 1, 'c1' ] ])
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

        self.filter_repo_and_check( [ 'a' ] )

        self.check_log_of_file_in_rev('a/bla', 2, [ [ 2, 'c3' ], [ 1, 'c1' ] ])
        self.assertEquals(env.get_log_of_revision(2), 'c3')

    def test_start_rev(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.change_file('a/bla', 'yyy')
        env.commit('c2')
        # Revision 3
        env.change_file('a/bla', 'zzz')
        env.commit('c3')

        self.filter_repo_and_check( [ '--start-rev', '2', 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'yyy', 'File a/bla correct in rev 1')
        self.check_log_of_file_in_rev('a/bla', 1, [ [ 1, 'c2' ] ])
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'zzz', 'File a/bla correct in rev 2')
        self.check_log_of_file_in_rev('a/bla', 2, [ [ 2, 'c3' ], [ 1, 'c2' ] ])

        
if __name__ == '__main__':
    unittest.main()
