
import unittest
import re
from StringIO import StringIO

from svn_repo_test_environment import TestEnvironment

from svnfiltereddump import SvnRepository

class TestSvnRepository(unittest.TestCase):
    env = None
    def setUp(self):
        if TestSvnRepository.env is None:
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
            env.commit('c3\nextra long\n')
            TestSvnRepository.env = env
        self.env = TestSvnRepository.env
        self.repo = SvnRepository(self.env.repo_path)

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

    def test_get_dump_file_handle_for_revision(self):
        fh = self.repo.get_dump_file_handle_for_revision(3)
        dump = fh.read()
        normalzied_dump = re.sub('UUID: \S+', 'UUID: XXX',
                          re.sub('svn:date\nV 27\n\S+', 'svn:date\nV 27\nYYY',
                          dump))
        self.assertEqual(normalzied_dump, """SVN-fs-dump-format-version: 2

UUID: XXX

Revision-number: 3
Prop-content-length: 117
Content-length: 117

K 7
svn:log
V 14
c3
extra long

K 10
svn:author
V 8
testuser
K 8
svn:date
V 27
YYY
PROPS-END

Node-path: a/x1
Node-kind: file
Node-action: add
Prop-content-length: 10
Text-content-length: 6
Text-content-md5: cde333fcdaa0fbf09280e457333d72fd
Text-content-sha1: 9558e4c4678259123b0553229c304db1a2ed4754
Content-length: 16

PROPS-END
x11111

Node-path: a/x2
Node-kind: file
Node-action: add
Prop-content-length: 10
Text-content-length: 6
Text-content-md5: 56a20ee450b0936c3a976dcdaddb2dd1
Text-content-sha1: e1b9077d3220006a05f7e740c6ce88bd242a0dfd
Content-length: 16

PROPS-END
x22222

Node-path: a/bla
Node-action: delete


""")

    def test_get_tree_handle_for_path(self):
        list = [ ]
        with self.repo.get_tree_handle_for_path('a', 3) as tree_handle:
            for item in tree_handle:
                list.append(item)
        self.assertEqual(list, [ "a/", "a/bla2", "a/x1", "a/x2" ])

    def test_get_revision_info(self):
        info = self.repo.get_revision_info(3)
        self.assertEqual(info.author, 'testuser')
        self.assertEqual(info.log_message, "c3\nextra long\n")

    def test_get_uuid(self):
        uuid = self.repo.get_uuid()
        self.assertEqual(uuid, self.env.uuid)

    def test_get_youngest_revision(self):
        last_rev = self.repo.get_youngest_revision()
        self.assertEqual(last_rev, 3)
