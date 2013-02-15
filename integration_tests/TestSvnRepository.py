
import unittest
import re
from StringIO import StringIO

from svn_repo_test_environment import TestEnvironment

from svnfiltereddump import SvnRepository, SvnDumpReader

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
        lumps = [ ]
        with self.repo.get_dump_file_handle_for_revision(3) as fh:
            reader = SvnDumpReader(fh)
            self._check_lump(
                reader.read_lump(),
                [ 'SVN-fs-dump-format-version', '2' ],
                { },
                None
            )
            self._check_lump(
                reader.read_lump(),
                [ 'UUID', 'XXX' ],
                { },
                None
            )
            self._check_lump(
                reader.read_lump(),
                [ 'Revision-number', '3' ],
                { 'svn:log': "c3\nextra long\n", 'svn:author': 'testuser', 'svn:date': 'XXX' },
                None
            )
            self._check_lump(
                reader.read_lump(),
                [ 'Node-path', 'a/x1', 'Node-kind', 'file', 'Node-action', 'add',
                  'Text-content-md5', 'cde333fcdaa0fbf09280e457333d72fd',
                  'Text-content-sha1', '9558e4c4678259123b0553229c304db1a2ed4754'
                ],
                { },
                'x11111'
            )
            self._check_lump(
                reader.read_lump(),
                [ 'Node-path', 'a/x2', 'Node-kind', 'file', 'Node-action', 'add',
                  'Text-content-md5', '56a20ee450b0936c3a976dcdaddb2dd1',
                  'Text-content-sha1', 'e1b9077d3220006a05f7e740c6ce88bd242a0dfd'
                ],
                { },
                'x22222'
            )

    def test_get_tree_handle_for_path(self):
        list = [ ]
        with self.repo.get_tree_handle_for_path('a', 3) as tree_handle:
            for item in tree_handle:
                list.append(item)
        self.assertEqual(sorted(list), [ "a/", "a/bla2", "a/x1", "a/x2" ])

    def test_get_revision_info(self):
        info = self.repo.get_revision_info(3)
        self.assertEqual(info.author, 'testuser')
        self.assertEqual(info.log_message, "c3\nextra long\n")
        if not re.search('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$', info.date):
            self.fail("Date '%s' expected format" % ( info.date ))

    def test_get_uuid(self):
        uuid = self.repo.get_uuid()
        self.assertEqual(uuid, self.env.uuid)

    def test_get_youngest_revision(self):
        last_rev = self.repo.get_youngest_revision()
        self.assertEqual(last_rev, 3)

    def _check_lump(self, lump, expected_headers, expected_properties, expected_text):
        headers = [ ]
        for key in lump.get_header_keys():
            if key in [ 'Content-length', 'Text-content-length', 'Prop-content-length' ]:
                continue
            expected_key = expected_headers[0];
            self.assertEqual(key, expected_key)
            expected_value = expected_headers[1]
            if expected_value != 'XXX':
                self.assertEqual(lump.get_header(key), expected_value)
            expected_headers = expected_headers[2:]
        self.assertEqual(expected_headers, []) 

        self.assertEqual(sorted(lump.properties.keys()), sorted(expected_properties.keys()))
        for key in lump.properties:
            if expected_properties[key] != 'XXX':
                self.assertEqual(lump.properties[key], expected_properties[key])

        if expected_text is None:
            self.assertEqual(lump.content, None)
        else:
            fh = StringIO()
            lump.content.empty_to(fh)
            fh.seek(0)
            self.assertEqual(fh.read(), expected_text)
