

from unittest import TestCase
from StringIO import StringIO
from svnfiltereddump import SvnDumpReader

class SvnDumpReaderTests(TestCase):

    def test_read_props_and_text(self):
        fh = StringIO("""
Node-path: bla
Node-kind: file
Node-action: add
Prop-content-length: 27
Text-content-length: 16
Text-content-md5: 4b6209c3b1032d515731c4f992fff73a
Text-content-sha1: a1d199953be4046ac8067ef1724ce5796a791fe3
Content-length: 43

K 4
blub
V 3
XXX
PROPS-END
fsdfa
fgasdfgsd


""")

        reader = SvnDumpReader(fh)
        lump = reader.read_lump()

        self.assertEqual(lump.get_header_keys(), [
            'Node-path', 'Node-kind', 'Node-action',
            'Prop-content-length', 'Text-content-length',
            'Text-content-md5', 'Text-content-sha1',
            'Content-length'
        ])
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties['blub'], 'XXX')
        out_fh = StringIO()
        lump.content.empty_to(out_fh)
        out_fh.seek(0)
        self.assertEqual(out_fh.read(), """fsdfa
fgasdfgsd
""")

    def test_read_props_only(self):
        fh = StringIO("""
Revision-number: 5
Prop-content-length: 107
Content-length: 107

K 7
svn:log
V 5
Test

K 10
svn:author
V 8
wilhelmh
K 8
svn:date
V 27
2011-09-09T15:42:21.809782Z
PROPS-END


""")

        reader = SvnDumpReader(fh)
        lump = reader.read_lump()

        self.assertEqual(lump.get_header_keys(), [
            'Revision-number', 'Prop-content-length', 'Content-length'
        ])
        self.assertEqual(lump.get_header('Revision-number'), '5')
        self.assertEqual(lump.properties['svn:log'], "Test\n")
        self.assertEqual(lump.properties['svn:author'], "wilhelmh")
        self.assertEqual(lump.properties['svn:date'], "2011-09-09T15:42:21.809782Z")
        self.assertEqual(lump.content, None)

    def test_read_text_only(self):
        fh = StringIO("""
Node-path: a
Node-kind: file
Node-action: change
Text-content-length: 2
Text-content-md5: 009520053b00386d1173f3988c55d192
Text-content-sha1: 9063a9f0e032b6239403b719cbbba56ac4e4e45f
Content-length: 2

y


""")

        reader = SvnDumpReader(fh)
        lump = reader.read_lump()

        self.assertEqual(lump.get_header_keys(), [
            'Node-path', 'Node-kind', 'Node-action',
            'Text-content-length', 'Text-content-md5', 'Text-content-sha1',
            'Content-length'
        ])
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.properties.keys(), [ ] )
        out_fh = StringIO()
        lump.content.empty_to(out_fh)
        out_fh.seek(0)
        self.assertEqual(out_fh.read(), "y\n")
