from unittest import TestCase
import tempfile
import os

from svnfiltereddump import Config


class ConfigTest(TestCase):

    def test_simple_args(self):
        config = Config(['/repo/path', 'a/b/c', 'x/y'])
        self.assertEqual(config.source_repository, '/repo/path')
        self.assertEqual(sorted(config.include_paths), ['a/b/c', 'x/y'])
        self.assertEqual(config.exclude_paths, [])
        self.assertEqual(config.keep_empty_revs, False)
        self.assertEqual(config.start_rev, None)
        self.assertEqual(config.quiet, False)
        self.assertEqual(config.log_file, None)
        self.assertEqual(config.create_parent_dirs, True)
        self.assertEqual(config.drop_old_tags_and_branches, False)

        self.assertTrue(config.is_path_tag_or_branch('tags/something'))
        self.assertTrue(config.is_path_tag_or_branch('prefix/tags/something'))
        self.assertTrue(config.is_path_tag_or_branch('blub/branches/bla'))

        self.assertFalse(config.is_path_tag_or_branch('blub/branches'))
        self.assertFalse(config.is_path_tag_or_branch('trunk'))
        self.assertFalse(config.is_path_tag_or_branch('bla'))
        self.assertFalse(config.is_path_tag_or_branch('tags'))
        self.assertFalse(config.is_path_tag_or_branch('tags/'))
        self.assertFalse(config.is_path_tag_or_branch('tagsX/something'))
        self.assertFalse(config.is_path_tag_or_branch('prefix/tags'))
        self.assertFalse(config.is_path_tag_or_branch('tags/something/bla'))
        self.assertFalse(config.is_path_tag_or_branch('prefix/branches/something/bla'))
        self.assertFalse(config.is_path_tag_or_branch('trunk/tags/x'))
        self.assertFalse(config.is_path_tag_or_branch('a/trunk/bla/branches/x'))

    def test_include_file(self):
        (fh) = tempfile.NamedTemporaryFile(delete=False)
        fh.write("a/x\nb/y\nc/z\n")
        fh.close()
        config = Config(['/repo/path', '--include-file', fh.name])
        self.assertEqual(config.source_repository, '/repo/path')
        self.assertEqual(sorted(config.include_paths), ['a/x', 'b/y', 'c/z'])
        self.assertEqual(config.exclude_paths, [])
        os.remove(fh.name)

    def test_include_file_plus(self):
        (fh) = tempfile.NamedTemporaryFile(delete=False)
        fh.write("a/x\nb/y\nc/z\n")
        fh.close()
        config = Config(['/repo/path', '--include-file', fh.name, 'x/y'])
        self.assertEqual(sorted(config.include_paths), ['a/x', 'b/y', 'c/z', 'x/y'])
        self.assertEqual(config.exclude_paths, [])
        os.remove(fh.name)

    def test_exclude(self):
        config = Config(['/repo/path', 'a/b/c', '--exclude', 'x/y'])
        self.assertEqual(sorted(config.include_paths), ['a/b/c'])
        self.assertEqual(config.exclude_paths, ['x/y'])

    def test_exclude_file_plus(self):
        (fh) = tempfile.NamedTemporaryFile(delete=False)
        fh.write("x1\nx2\n")
        fh.close()
        config = Config(['/repo/path', 'a/b/c', '--exclude-file', fh.name, '--exclude', 'x/y'])
        self.assertEqual(config.include_paths, ['a/b/c'])
        self.assertEqual(sorted(config.exclude_paths), ['x/y', 'x1', 'x2'])
        os.remove(fh.name)

    def test_keep_empty_revs(self):
        config = Config(['/repo/path', 'a/b', '--keep-empty-revs'])
        self.assertEqual(config.keep_empty_revs, True)

    def test_quiet(self):
        config = Config(['/repo/path', 'a/b', '--quiet'])
        self.assertEqual(config.quiet, True)

    def test_q(self):
        config = Config(['/repo/path', 'a/b', '-q'])
        self.assertEqual(config.quiet, True)

    def test_log_file(self):
        config = Config(['/repo/path', 'a/b', '--log-file=/some/file'])
        self.assertEqual(config.log_file, '/some/file')

    def test_l(self):
        config = Config(['/repo/path', 'a/b', '-l', '/some/file'])
        self.assertEqual(config.log_file, '/some/file')

    def test_no_extra_mkdirs(self):
        config = Config(['/repo/path', 'a/b', '--no-extra-mkdirs'])
        self.assertEqual(config.create_parent_dirs, False)

    def test_drop_old_tags_and_branches(self):
        config = Config(['/repo/path', 'a/b', '--drop-old-tags-and-branches'])
        self.assertTrue(config.drop_old_tags_and_branches)

    def test_custom_tag_and_branches(self):
        config = Config(['/repo/path', 'a/b', '--tag-or-branch-dir', 'bla', '--tag-or-branch-dir', 'branches'])
        self.assertTrue(config.is_path_tag_or_branch('foo/bla/bar'))
        self.assertTrue(config.is_path_tag_or_branch('foo/branches/bar'))
        self.assertFalse(config.is_path_tag_or_branch('foo/trunk/bar'))
        self.assertFalse(config.is_path_tag_or_branch('foo/tags/bar'))

    def test_custom_trunk(self):
        config = Config(['/repo/path', 'a/b', '--trunk-dir', 'bla', '--tag-or-branch-dir', 'blub'])
        self.assertFalse(config.is_path_tag_or_branch('bla/branches/bar'))
        self.assertFalse(config.is_path_tag_or_branch('blub/branches/bar'))
        self.assertFalse(config.is_path_tag_or_branch('trunk/branches/bar'))

    # We need: 'assertExits' here!!
    # def test_bad_source_repo_path(self):
    #    self.assertRaises(Exception, Config, [ 'repo/path', 'a/b' ])
