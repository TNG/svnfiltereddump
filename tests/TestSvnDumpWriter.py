
from unittest import TestCase
from StringIO import StringIO
from svnfiltereddump import SvnDumpWriter
from svnfiltereddump import SvnLump
from svnfiltereddump import ContentTin

class SvnDumpWriterTests(TestCase):

    def setUp(self):
        self.output = StringIO()
        self.writer =  SvnDumpWriter(
            file_handle = self.output
        )

    def test_simple(self):
        lump = SvnLump()
        lump.set_header('header1', 'value1')
        lump.set_header('header2', 'value2')

        self.writer.write_lump(lump)

        self.output.seek(0)
        self.assertEqual(self.output.read(), """header1: value1
header2: value2

"""
        )

    def test_properties_only(self):
        lump = SvnLump()
        lump.set_header('header1', 'value1')
        lump.set_header('header2', 'value2')
        lump.properties['prop1'] = "zzz\nyyy\n"
        lump.properties['second_property'] = 'abc'

        self.writer.write_lump(lump)

        self.output.seek(0)
        self.assertEqual(self.output.read(), """header1: value1
header2: value2

K 5
prop1
V 8
zzz
yyy

K 15
second_property
V 3
abc
PROPS-END

"""
        )

    def test_text_only(self):
        lump = SvnLump()
        lump.set_header('Node-path', 'a')
        lump.set_header('Node-kind', 'file')
        lump.set_header('Node-action', 'change')
        lump.set_header('Text-content-length', '2')
        lump.set_header('Text-content-md5', '009520053b00386d1173f3988c55d192')
        lump.set_header('Text-content-sha1', '9063a9f0e032b6239403b719cbbba56ac4e4e45f')
        lump.set_header('Content-length', 2)
        content_fh = StringIO("y\n")
        lump.content = ContentTin(content_fh, 2, '009520053b00386d1173f3988c55d192')
        
        self.writer.write_lump(lump)

        self.output.seek(0)
        self.assertEqual(self.output.read(), """Node-path: a
Node-kind: file
Node-action: change
Text-content-length: 2
Text-content-md5: 009520053b00386d1173f3988c55d192
Text-content-sha1: 9063a9f0e032b6239403b719cbbba56ac4e4e45f
Content-length: 2

y


"""
        )

    def test_text_and_properties(self):
        lump = SvnLump()
        lump.set_header('Node-path', 'bla')
        lump.set_header('Node-kind', 'file')
        lump.set_header('Node-action', 'add')
        lump.set_header('Text-content-length', 16)
        lump.properties['blub'] = "XXX"
        content_fh = StringIO("fsdfa\nfgasdfgsd\n")
        lump.content = ContentTin(content_fh, 16, 'FAKEMD5SUM')

        self.writer.write_lump(lump)

        self.output.seek(0)
        self.assertEqual(self.output.read(), """Node-path: bla
Node-kind: file
Node-action: add
Text-content-length: 16

K 4
blub
V 3
XXX
PROPS-END
fsdfa
fgasdfgsd


"""
        )
