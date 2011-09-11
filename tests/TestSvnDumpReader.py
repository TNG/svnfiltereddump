

from unittest import TestCase
from StringIO import StringIO
from svnfiltereddump import SvnDumpReader

class SvnDumpReaderTests(TestCase):

    def test_read(self):
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
