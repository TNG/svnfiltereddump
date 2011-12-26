
import unittest
from subprocess import call

from functional_test_environment import TestEnvironment


class ComandLineFeatureTests(unittest.TestCase):
    
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
        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'xxx', 'File a/bla correct in rev 1')
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'zzz', 'File a/bla correct in rev 2')
        self.assertEquals(env.get_property_in_rev('a/bla', 2, 'some_prop'), 'prop_value', 'File a/bla property correct in rev 2')
        self.check_log_of_file_in_rev('a/bla', 2, [ [ 2, 'c2' ], [ 1, 'c1' ] ])

    def test_quiet(self):
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

        env.filter_repo( [ '-q', 'a' ] )

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

        env.filter_repo( [ 'x/a', 'x/foo' ] ) 

        self.assertTrue(env.is_existing_in_rev('x/a/bla', 1), 'File bla was copied')
        self.assertTrue(env.is_existing_in_rev('x/foo', 1), 'File foo was copied')
        self.assertFalse(env.is_existing_in_rev('x/b/blub', 1), 'File blub was NOT copied')
        self.assertFalse(env.is_existing_in_rev('x/bar', 1), 'File bar was NOT copied')

    def test_include_with_no_mkdirs(self):
        env = self.env
        env.mkdir('x/a')
        env.mkdir('x/b')
        env.add_file('x/a/bla', 'xxx')
        env.add_file('x/b/blub', 'yyy')
        env.add_file('x/foo', 'zzz')
        env.add_file('x/bar', 'ZZZ')
        env.commit('c1')

        env.mkdir_target('x') # Rev 1 in target

        env.filter_repo( [ '--no-extra-mkdirs', 'x/a', 'x/foo' ] ) 

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

        include_file = env.create_tmp_file("x/a\n" + "x/foo\n")

        env.filter_repo( [ '--include-file', include_file ] ) 

        self.assertTrue(env.is_existing_in_rev('x/a/bla', 1), 'File bla was copied')
        self.assertTrue(env.is_existing_in_rev('x/foo', 1), 'File foo was copied')
        self.assertFalse(env.is_existing_in_rev('x/b/blub', 1), 'File blub was NOT copied')
        self.assertFalse(env.is_existing_in_rev('x/bar', 1), 'File bar was NOT copied')

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

        env.filter_repo( [ 'a', '--keep-empty-revs' ] )

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

        env.filter_repo( [ 'a' ] )

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

        env.filter_repo( [ '--start-rev', '2', 'a' ] )

        self.assertEquals(env.get_file_content_in_rev('a/bla', 1), 'yyy', 'File a/bla correct in rev 1')
        self.check_log_of_file_in_rev('a/bla', 1, [ [ 1, 'svnfiltereddump boots trap revision' ] ])
        self.assertEquals(env.get_file_content_in_rev('a/bla', 2), 'zzz', 'File a/bla correct in rev 2')
        self.check_log_of_file_in_rev('a/bla', 2, [ [ 2, 'c3' ], [ 1, 'svnfiltereddump boots trap revision' ] ])

    def test_drop_old_tags_and_branches(self):
        env = self.env
        # Revision dropped
        env.mkdir('trunk')
        env.mkdir('tags')
        env.mkdir('branches')
        env.add_file('trunk/bla', 'xxx')
        env.commit('c1')
        # Revision dropped
        env.update()
        env.copy_path('trunk', 'branches/very_old');
        env.copy_path('trunk', 'tags/OLD1');
        env.commit('c2')
        # Revision 1 --- start_rev ---
        env.copy_path('trunk', 'branches/still_old');
        env.commit('c3')
        # Revision 2
        env.update()
        env.change_file('trunk/bla', 'zzz')
        env.change_file('branches/still_old/bla', 'yyy');
        env.commit('c4')
        # Revision 3
        env.update()
        env.copy_path('trunk', 'branches/new');
        env.copy_path('trunk', 'tags/NEW1');
        env.move_path('tags/OLD1', 'tags/RENAMED_BUT_STILL_OLD')
        env.change_file('branches/new/bla', 'zzz1')
        env.commit('c5')

        env.filter_repo( [ '--start-rev', '3', '--drop-old-tags-and-branches', '/' ] )

        self.assertEqual(env.get_file_content_in_rev('trunk/bla', 1), 'xxx', 'File trunk/bla correct in rev 1')
        self.assertEqual(env.get_file_content_in_rev('trunk/bla', 2), 'zzz', 'File trunk/bla correct in rev 2')
        self.check_log_of_file_in_rev('trunk/bla', 3, [ [ 2, 'c4' ], [ 1, 'svnfiltereddump boots trap revision' ] ] )

        self.assertEqual(env.get_file_content_in_rev('branches/new/bla', 3), 'zzz1', 'File branches/new/bla correct in rev 3')
        self.assertEqual(env.get_file_content_in_rev('tags/NEW1/bla', 3), 'zzz', 'File tags/NEW1/bla correct in rev 2')
        
        self.assertFalse(env.is_existing_in_rev('branches/very_old', 1), 'Very old brach dropped')
        self.assertFalse(env.is_existing_in_rev('branches/still_old', 1), 'Still old brach dropped')
        self.assertFalse(env.is_existing_in_rev('tags/OLD1', 1), 'Old tag dropped')
        self.assertFalse(env.is_existing_in_rev('tags/RENAMED_BUT_STILL_OLD', 3), 'Renamed old tag dropped')

    def test_drop_old_tags_and_branches_custom_names(self):
        env = self.env
        # Revision dropped
        env.mkdir('my_tags')
        env.mkdir('my_branches')
        env.mkdir('tags')
        env.mkdir('branches')
        env.mkdir('trunk')
        env.add_file('trunk/bla', 'xxx')
        env.commit('c1')
        # Revision dropped
        env.copy_path('trunk', 'my_tags/OLD_TAG')
        env.copy_path('trunk', 'my_branches/OLD_BRANCH')
        env.copy_path('trunk', 'tags/not_really_a_tag')
        env.copy_path('trunk', 'branches/not_really_a_branch')
        env.commit('c2')
        # Revision 1 --- start_rev ---
        env.add_file('boring', 'zzz')
        env.commit('c3')

        env.filter_repo( [
            '--start-rev', '3', '--drop-old-tags-and-branches',
            '--tag-or-branch-dir', 'my_tags', '--tag-or-branch-dir', 'my_branches', '/'
        ] )

        self.assertEquals(env.get_file_content_in_rev('trunk/bla', 1), 'xxx', 'File trunk/bla correct in rev 1')
        self.assertEquals(env.get_file_content_in_rev('tags/not_really_a_tag/bla', 1), 'xxx', 'File tags/not_really_a_tag/bla correct in rev 1')
        self.assertEquals(env.get_file_content_in_rev('branches/not_really_a_branch/bla', 1), 'xxx', 'File branches/not_really_a_branch/bla correct in rev 1')
        
        self.assertFalse(env.is_existing_in_rev('my_tags/OLD_TAG', 1), 'Old tag dropped')
        self.assertFalse(env.is_existing_in_rev('my_branches/OLD_BRANCH', 1), 'Old branch dropped')

    def test_drop_old_tags_and_branches_with_custom_trunk(self):
        env = self.env
        # Revision dropped
        env.mkdir('mytrunk')
        env.mkdir('tags')
        env.mkdir('branches')
        env.add_file('mytrunk/bla', 'xxx')
        env.commit('c1')
        # Revision dropped
        env.mkdir('mytrunk/tags')
        env.mkdir('mytrunk/tags/no_tag')
        env.add_file('mytrunk/tags/no_tag/blub', 'yyy')
        env.mkdir('trunk')
        env.mkdir('trunk/branches')
        env.copy_path('mytrunk', 'branches/OLD_BRANCH'); # Valid old branch because 'trunk' is not magic in this time
        env.commit('c2')
        # Revision dropped
        env.update()
        env.copy_path('mytrunk', 'tags/OLD1'); # Valid old tag
        env.commit('c3')
        # Revision 1 --- start_rev ---
        env.change_file('mytrunk/bla', 'zzz')
        env.commit('c4')
        # Revision 3
        env.update()
        env.copy_path('mytrunk', 'trunk/branches/NEW'); # Valid recent branch
        env.commit('c5')

        env.filter_repo( [ '--start-rev', '4', '--drop-old-tags-and-branches', '/', '--trunk-dir', 'mytrunk' ] )

        self.assertEqual(env.get_file_content_in_rev('mytrunk/bla', 2), 'zzz')
        self.assertEqual(env.get_file_content_in_rev('mytrunk/tags/no_tag/blub', 2), 'yyy')
        self.assertEqual(env.get_file_content_in_rev('trunk/branches/NEW/bla', 2), 'zzz')
        self.assertEqual(env.get_file_content_in_rev('trunk/branches/NEW/tags/no_tag/blub', 2), 'yyy')

        self.assertFalse(env.is_existing_in_rev('branches/OLD_BRANCH', 1), 'Very old brach dropped')
        self.assertFalse(env.is_existing_in_rev('tags/OLD1', 1), 'Old tag dropped')

if __name__ == '__main__':
    unittest.main()
