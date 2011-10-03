
import unittest
from subprocess import call

from functional_test_environment import TestEnvironment


class ScenarioTests(unittest.TestCase):
    
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
            self.assertEquals(
                parsed_log, exected_log,
                "Validate log of file file %s in revision %d" % ( name, rev )
            )
        else:
            self.fail(
                "Failed to get log of file %s in revision %d with error:\n%s"
                %  ( name, rev, error )
            )

    def test_add_in_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.propset('a/bla', 'some_prop', 'prop_value')
        env.commit('c1')
        # Revision 2
        env.copy_file('a/bla', 'a/blub')
        env.commit('c2')

        self.filter_repo_and_check( [ 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'xxx', 'File a/bla correct in rev 1')
        self.assertFalse(env.is_existing_in_rev('a/blub', 1), 'File blub not existent in rev 1')
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'xxx', 'File a/bla correct in rev 2')
        self.assertEquals(env.get_file_content_in_rev('a/blub', 2), 'xxx', 'File a/blub correct in rev 2')
        self.assertEquals(env.get_property_in_rev('a/blub', 2, 'some_prop'), 'prop_value', 'File a/blub property correct in rev 2')
        self.check_log_of_file_in_rev('a/blub', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_add_into_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('b')
        env.add_file('a/bla', 'xxx')
        env.propset('a/bla', 'some_prop', 'prop_value')
        env.commit('c1')
        # Revision 2
        env.copy_file('a/bla', 'b/blub')
        env.commit('c2')

        self.filter_repo_and_check( [ 'b' ] )

        self.assertFalse(env.is_existing_in_rev('a/bla', 1), 'File bla not existent in rev 2')
        self.assertEquals(env.get_file_content_in_rev('b/blub', 2), 'xxx', 'File b/blub correct in rev 2')
        self.assertEquals(env.get_property_in_rev('b/blub', 2, 'some_prop'), 'prop_value', 'File b/blub property correct in rev 2')
        self.check_log_of_file_in_rev('b/blub', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])
        
    def test_add_into_excluded(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('b')
        env.mkdir('b/x')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.copy_file('a/bla', 'b/x/blub')
        env.commit('c2')

        self.filter_repo_and_check( [ 'b', '--exclude', 'b/x' ] )

        self.assertFalse(env.is_existing_in_rev('b/x/blub', 1), 'File blub not existent in rev 2')

    def test_del_whole_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.rm_file('a')
        env.commit('c2')

        self.filter_repo_and_check( [ 'a' ] )

        self.assertTrue(env.is_existing_in_rev('a/bla', 1), 'File bla existent in rev 1')
        self.assertTrue(env.is_existing_in_rev('a', 2), 'Dir a not existent in rev 2')
        
    def tesl_del_in_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('a/b')
        env.add_file('a/b/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.rm_file('a/b')
        env.commit('c2')

        self.filter_repo_and_check( [ 'a' ] )

        self.assertTrue(env.is_existing_in_rev('a/b/bla', 1), 'File bla existent in rev 1')
        self.assertTrue(env.is_existing_in_rev('a/b', 2), 'Dir a/b not existent in rev 2')

    def test_del_over_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('a/b')
        env.add_file('a/b/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.rm_file('a')
        env.commit('c2')

        env.mkdir_target('a') # Rev 1 in target

        self.filter_repo_and_check( [ 'a/b' ] )

        self.assertTrue(env.is_existing_in_rev('a/b/bla', 2), 'File bla existent in rev 2')
        self.assertTrue(env.is_existing_in_rev('a/b', 3), 'Dir a/b not existent in rev 3')

    def test_change_in_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.change_file('a/bla', 'yyy')
        env.commit('c2')

        self.filter_repo_and_check( [ 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'xxx', 'File a/bla correct in rev 1')
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'yyy', 'File a/bla correct in rev 2')
        
    def test_add_and_change_in_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.copy_file('a/bla', 'a/blub')
        env.change_file('a/blub', 'yyy')
        env.commit('c2')

        self.filter_repo_and_check( [ 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/blub', 2), 'yyy', 'File a/blub correct in rev 2')
        self.check_log_of_file_in_rev('a/blub', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_add_and_change_into_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('b')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.copy_file('a/bla', 'b/blub')
        env.change_file('b/blub', 'yyy')
        env.commit('c2')

        self.filter_repo_and_check( [ 'b' ] )

        self.assertEquals(env.get_file_content_in_rev('b/blub', 2), 'yyy', 'File a/blub correct in rev 2')
        self.check_log_of_file_in_rev('b/blub', 2, [ [ 2, 'c2' ] ])

if __name__ == '__main__':
    unittest.main()
