
import unittest
from subprocess import call

from functional_test_environment import TestEnvironment


class ScenarioTests(unittest.TestCase):
    
    def setUp(self):
        self.env = TestEnvironment()

    def tearDown(self):
        self.env.destroy()

    def check_log_of_file_in_rev(self, name, rev, exected_log):
        ( parsed_log, error ) = self.env.get_log_of_file_in_rev(name, rev)
        if error is None:
            self.assertEquals(parsed_log, exected_log)
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
        env.copy_path('a/bla', 'a/blub')
        env.commit('c2')

        env.filter_repo( [ 'a' ] )

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
        env.copy_path('a/bla', 'b/blub')
        env.commit('c2')

        env.filter_repo( [ 'b' ] )

        self.assertFalse(env.is_existing_in_rev('a/bla', 1), 'File bla not existent in rev 1')
        self.assertEquals(env.get_file_content_in_rev('b/blub', 2), 'xxx', 'File b/blub correct in rev 2')
        self.assertEquals(env.get_property_in_rev('b/blub', 2, 'some_prop'), 'prop_value', 'File b/blub property correct in rev 2')
        self.check_log_of_file_in_rev('b/blub', 2, [ [ 2, 'c2' ] ])
        
    def test_add_dir_above_file_inside_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('a/b')
        env.add_file('a/b/bla', 'xxx')
        env.propset('a/b/bla', 'some_prop', 'prop_value')
        env.commit('c1')
        # Revision 2
        env.copy_path('a', 'c')
        env.commit('c2')

        env.filter_repo( [ 'a', 'c/b' ] )

        self.assertTrue(env.is_existing_in_rev('a/b/bla', 1), 'File a/b/bla existent in rev 1')
        self.assertFalse(env.is_existing_in_rev('c/b/bla', 1), 'File c/b/bla not existent in rev 1')
        self.assertEquals(env.get_file_content_in_rev('c/b/bla', 2), 'xxx', 'File bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('c/b/bla', 2, 'some_prop'), 'prop_value', 'File bla property correct in rev 2')
        self.check_log_of_file_in_rev('c/b/bla', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_add_dir_above_dir_inside_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('a/b')
        env.mkdir('a/b/x')
        env.add_file('a/b/x/bla', 'xxx')
        env.propset('a/b/x', 'some_prop', 'prop_value')
        env.commit('c1')
        # Revision 2
        env.copy_path('a', 'c')
        env.commit('c2')

        env.filter_repo( [ 'a', 'c/b' ] )

        self.assertTrue(env.is_existing_in_rev('a/b/x/bla', 1), 'File a/b/x/bla existent in rev 1')
        self.assertFalse(env.is_existing_in_rev('c/b/x/bla', 1), 'File c/b/x/bla not existent in rev 1')
        self.assertEquals(env.get_file_content_in_rev('c/b/x/bla', 2), 'xxx', 'File bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('c/b/x', 2, 'some_prop'), 'prop_value', 'Dir x property correct in rev 2')
        self.check_log_of_file_in_rev('c/b/x/bla', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_add_dir_above_file_into_target(self):
        env = self.env
        # Revision 1 - extra mkdirs only
        env.mkdir('a')
        env.mkdir('a/b')
        env.add_file('a/b/bla', 'xxx')
        env.propset('a/b/bla', 'some_prop', 'prop_value')
        env.commit('c1')
        # Revision 2
        env.copy_path('a', 'c')
        env.commit('c2')

        env.filter_repo( [ 'c/b' ] )

        self.assertFalse(env.is_existing_in_rev('a', 1), 'Dir a not existent in rev 1')
        self.assertEquals(env.get_file_content_in_rev('c/b/bla', 2), 'xxx', 'File bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('c/b/bla', 2, 'some_prop'), 'prop_value', 'File bla property correct in rev 2')
        self.check_log_of_file_in_rev('c/b/bla', 2, [ [ 2, 'c2' ] ])

    def test_add_dir_above_dir_into_target(self):
        env = self.env
        # Revision 1 - extra mkdirs only
        env.mkdir('a')
        env.mkdir('a/b')
        env.mkdir('a/b/x')
        env.add_file('a/b/x/bla', 'xxx')
        env.propset('a/b/x', 'some_prop', 'prop_value')
        env.commit('c1')
        # Revision 1
        env.copy_path('a', 'c')
        env.commit('c2')

        env.filter_repo( [ 'c/b' ] )

        self.assertFalse(env.is_existing_in_rev('a', 2), 'Dir a not existent in rev 2')
        self.assertEquals(env.get_file_content_in_rev('c/b/x/bla', 2), 'xxx', 'File bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('c/b/x', 2, 'some_prop'), 'prop_value', 'Dir x property correct in rev 2')
        self.check_log_of_file_in_rev('c/b/x/bla', 2, [ [ 2, 'c2' ] ])

    def test_add_into_excluded(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('b')
        env.mkdir('b/x')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.copy_path('a/bla', 'b/x/blub')
        env.commit('c2')

        env.filter_repo( [ 'b', '--exclude', 'b/x' ] )

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

        env.filter_repo( [ 'a' ] )

        self.assertTrue(env.is_existing_in_rev('a/bla', 1), 'File bla existent in rev 1')
        self.assertFalse(env.is_existing_in_rev('a', 2), 'Dir a not existent in rev 2')
        
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

        env.filter_repo( [ 'a' ] )

        self.assertTrue(env.is_existing_in_rev('a/b/bla', 1), 'File bla existent in rev 1')
        self.assertFalse(env.is_existing_in_rev('a/b', 2), 'Dir a/b not existent in rev 2')

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

        env.filter_repo( [ 'a/b' ] )

        self.assertTrue(env.is_existing_in_rev('a/b/bla', 1), 'File bla existent in rev 1')
        self.assertFalse(env.is_existing_in_rev('a/b', 2), 'Dir a/b not existent in rev 2')

    def test_change_in_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.change_file('a/bla', 'yyy')
        env.commit('c2')

        env.filter_repo( [ 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'xxx', 'File a/bla correct in rev 1')
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'yyy', 'File a/bla correct in rev 2')
        
    def test_add_and_change_in_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.copy_path('a/bla', 'a/blub')
        env.change_file('a/blub', 'yyyy') # Work around a stange Subversion 1.7.0 timing issue - change the size
        env.commit('c2')

        env.filter_repo( [ 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/blub', 2), 'yyyy')
        self.check_log_of_file_in_rev('a/blub', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_add_and_change_into_target(self):
        env = self.env
        # Revision 1
        env.mkdir('a')
        env.mkdir('b')
        env.add_file('a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.copy_path('a/bla', 'b/blub')
        env.change_file('b/blub', 'yyyy')
        env.commit('c2')

        env.filter_repo( [ 'b' ] )

        self.assertEquals(env.get_file_content_in_rev('b/blub', 2), 'yyyy', 'File a/blub correct in rev 2')
        self.check_log_of_file_in_rev('b/blub', 2, [ [ 2, 'c2' ] ])

    def test_drop_old_tags_and_branches_with_mixed_revisions(self):
        # The special thing in this test are the missing 'svn update' commands
        # before branch/tag creation. The actual behaviour is NOT desirable
        # - but we can't do any better in this case!
        env = self.env
        # Revision dropped
        env.mkdir('trunk')
        env.mkdir('tags')
        env.mkdir('branches')
        env.add_file('trunk/bla', 'xxx')
        env.commit('c1')
        # Revision 1 --- start_rev ---
        env.change_file('trunk/bla', 'zzz')
        env.commit('c2')
        # Revision 2
        env.copy_path('trunk', 'branches/new');
        env.copy_path('trunk', 'tags/NEW1');
        env.commit('c3')
        # Dropped as empty
        env.change_file('branches/new/bla', 'zzz1')
        env.commit('c4')

        env.filter_repo( [ '--start-rev', '2', '--drop-old-tags-and-branches', '/' ] )

        self.assertEquals(env.get_file_content_in_rev('trunk/bla', 1), 'zzz', 'File trunk/bla correct in rev 1')
        self.check_log_of_file_in_rev('trunk/bla', 1, [ [ 1, 'svnfiltereddump boots trap revision' ] ])
        
        self.assertFalse(env.is_existing_in_rev('branches/new', 1), 'Sorry - new but classified as old due to mixed revisions working copy (1)')
        self.assertFalse(env.is_existing_in_rev('tags/NEW1', 1), 'Sorry - new but classified as old due to mixed revisions working copy (1)')

    def test_tag_copy_current(self):
        env = self.env
        # Revision dropped
        env.mkdir('trunk')
        env.mkdir('tags')
        env.mkdir('branches')
        env.mkdir('trunk/a')
        env.mkdir('trunk/a/b')
        env.add_file('trunk/a/b/bla', 'xxx')
        env.commit('c1')
        # Revision 1 --- start_rev ---
        env.change_file('trunk/a/b/bla', 'yyy')
        env.commit('c2')
        # Revision 2
        env.change_file('trunk/a/b/bla', 'zzz')
        env.commit('c3')
        # Revision 3
        env.update()
        env.copy_path('trunk', 'tags/NEW1');
        env.commit('c4')
        # Revision 4
        env.change_file('trunk/a/b/bla', 'ZZZ')
        env.commit('c5')

        env.filter_repo( [ '--start-rev', '2', '--drop-old-tags-and-branches', 'trunk/a', 'tags/NEW1/a' ] )

        self.assertEquals(env.get_file_content_in_rev('trunk/a/b/bla', 4), 'ZZZ')
        self.check_log_of_file_in_rev('trunk/a/b/bla', 4, [ [ 4, 'c5' ], [2, 'c3' ], [ 1, 'svnfiltereddump boots trap revision' ] ])
        self.check_log_of_file_in_rev('tags/NEW1/a/b/bla', 4, [ [ 3, 'c4' ], [2, 'c3' ], [ 1, 'svnfiltereddump boots trap revision' ] ])
        
    def test_tag_copy_obsolete(self):
        env = self.env
        # Revision dropped
        env.mkdir('trunk')
        env.mkdir('tags')
        env.mkdir('branches')
        env.mkdir('trunk/a')
        env.mkdir('trunk/a/b')
        env.add_file('trunk/a/b/bla', 'xxx')
        env.commit('c1')
        # Revision dropped
        env.change_file('trunk/a/b/bla', 'yyy')
        env.commit('c2')
        # Revision dropped
        env.update()
        env.copy_path('trunk', 'tags/NEW1');
        env.commit('c3')
        # Revision 1 --- start_rev ---
        env.change_file('trunk/a/b/bla', 'zzz')
        env.commit('c4')
        # Revision 2
        env.change_file('trunk/a/b/bla', 'ZZZ')
        env.commit('c5')

        env.filter_repo( [ '--start-rev', '4', '--drop-old-tags-and-branches', 'trunk/a', 'tags' ] )

        self.assertEquals(env.get_file_content_in_rev('trunk/a/b/bla', 2), 'ZZZ')
        self.check_log_of_file_in_rev('trunk/a/b/bla', 2, [ [2, 'c5' ], [ 1, 'svnfiltereddump boots trap revision' ] ])
        self.assertFalse(env.is_existing_in_rev('tags/NEW1', 2), 'Obsolete branch dropped')

    def test_copy_in_from_ignored_revision(self):
        env = self.env
        # Revision 1
        env.mkdir('interesting')
        env.mkdir('boring')
        env.add_file('boring/bla', 'xxx')
        env.commit('c1')
        # Revision dropped - all boring
        env.add_file('boring/x1', '1')
        env.commit('c2')
        # Revision dropped - all boring
        env.change_file('boring/bla', 'yyy')
        env.commit('c3')
        env.update() # !!!!
        # Revision dropped - all boring
        env.add_file('boring/x2', '2')
        env.commit('c4')
        # Revision 2
        env.add_file('interesting/blub', 'abc')
        env.commit('c5')
        # Revision 3
        env.change_file('interesting/blub', 'cba')
        env.commit('c6')
        # Revision 4 - based on dropped revison
        env.copy_path('boring/bla', 'interesting/bla');
        env.commit('c7')

        env.filter_repo( [ 'interesting' ] )

        self.assertEquals(env.get_file_content_in_rev('interesting/bla', 4), 'yyy')
        self.check_log_of_file_in_rev('interesting/bla', 4, [ [4, 'c7' ] ])

    def test_basic_replace(self):
        env = self.env
        # Revision 1
        env.mkdir('interesting')
        env.add_file('interesting/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.rm_file('interesting/bla')
        env.add_file('interesting/bla', 'yyy')
        env.commit('c2')
       
        env.filter_repo( [ 'interesting' ] )
        
        self.assertEquals(env.get_file_content_in_rev('interesting/bla', 1), 'xxx')
        self.assertEquals(env.get_file_content_in_rev('interesting/bla', 2), 'yyy')
        self.check_log_of_file_in_rev('interesting/bla', 2, [ [2, 'c2' ] ])

    def test_replace_dir(self):
        env = self.env
        # Revision 1
        env.mkdir('interesting')
        env.mkdir('interesting/a')
        env.add_file('interesting/a/bla', 'xxx')
        env.commit('c1')
        # Revision 2
        env.rm_file('interesting/a')
        env.mkdir('interesting/a')
        env.add_file('interesting/a/blub', 'yyy')
        env.commit('c2')
       
        env.filter_repo( [ 'interesting' ] )
        
        self.assertEquals(env.get_file_content_in_rev('interesting/a/bla', 1), 'xxx')
        self.assertEquals(env.get_file_content_in_rev('interesting/a/blub', 2), 'yyy')
        self.assertFalse(env.is_existing_in_rev('interesting/a/blub', 1), 'File blub not existent in rev 1')
        self.assertFalse(env.is_existing_in_rev('interesting/a/bla', 2), 'File bla not existent in rev 2')
        self.check_log_of_file_in_rev('interesting/a/blub', 2, [ [2, 'c2' ] ])

    def test_brocken_merge_tracking(self):
        env = self.env
        # Revision 1 - dropped
        env.mkdir('trunk')
        env.add_file('trunk/bla', 'xxx')
        env.mkdir('branches')
        env.commit('c1')
        # Revision 2 - dropped
        env.copy_path('trunk', 'branches/obsolete')
        env.commit('c2')
        # Revision 3 - dropped
        env.change_file('branches/obsolete/bla', 'yyy')
        env.commit('c3')
        # Revision 4 -> New Revision 1
        env.add_file('branches/obsolete/blub', 'abc')
        env.commit('c4')
        # Revision 5 -> New Revision 2
        env.update()
        env.merge_reintegrate('^/branches/obsolete', 'trunk')
        env.commit('c5')
        # Revision 6 -> New Revision 3
        env.change_file('trunk/bla', 'zzz')
        env.commit('c6')

        env.filter_repo( [ '--start-rev', '4', '--drop-old-tags-and-branches', '/' ] )

        self.assertEquals(
            env.get_file_content_in_rev('trunk/bla', 2),
            'yyy',
            'Merge was done (bla)'
        )
        self.assertEquals(
            env.get_file_content_in_rev('trunk/blub', 2),
            'abc',
            'Merge was done (blub)'
        )
        self.assertFalse(
            env.is_existing_in_rev('branches/obsolete', 1),
            'Obsolete branch was dropped'
        )
        self.assertEquals(
            env.get_file_content_in_rev('trunk/bla', 3),
            'zzz',
            'Filter continued after broken merge info'
        )
    def test_zero_length_commit(self):
        env = self.env
        env.add_file('bla', '')
        env.commit('c1')

        env.filter_repo( [ '/' ] )

        self.assertEquals(
            env.get_file_content_in_rev('bla', 1),
            '',
            'Empty files work'
        )

if __name__ == '__main__':
    unittest.main()
