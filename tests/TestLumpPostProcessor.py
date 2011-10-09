
from unittest import TestCase
from StringIO import StringIO

from svnfiltereddump import Config, LumpPostProcessor, ContentTin, SvnLump

from DumpWriterMock import DumpWriterMock

class ParentDirectoryGeneratorMock(object):
    def __init__(self, writer):
        self.writer = writer
    def write_lumps(self):
        for marker in [ '1of2', '2of2' ]:
            lump = SvnLump()
            lump.set_header('ParentDirectoryGeneratorMockLump', marker)
            self.writer.write_lump(lump)

class TestLumpPostProcessor(TestCase):
    def setUp(self):
        self.config = Config( [ '--no-extra-mkdirs', '/dummy' ] )
        self.writer = DumpWriterMock(self)
        self.processor = LumpPostProcessor(self.config, self.writer)
        self.processor.parent_directory_lump_generator = ParentDirectoryGeneratorMock(self.processor)

    def test_dont_drop_empty_revs(self):
        self.config.keep_empty_revs = True

        lump = SvnLump()
        lump.set_header('Revision-number', '12')
        self.processor.write_lump(lump)

        lump = SvnLump()
        lump.set_header('Revision-number', '13')
        self.processor.write_lump(lump)

        lump = SvnLump()
        lump.set_header('Node-kind', 'file')
        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 3)
        self.assertEqual(self.writer.lumps[0].get_header('Revision-number'), '12')
        self.assertEqual(self.writer.lumps[1].get_header('Revision-number'), '13')
        self.assertEqual(self.writer.lumps[2].get_header('Node-kind'), 'file')

    def test_drop_empty_revs(self):
        lump = SvnLump()
        lump.set_header('Revision-number', '12')
        self.processor.write_lump(lump)

        lump = SvnLump()
        lump.set_header('Revision-number', '13')
        self.processor.write_lump(lump)

        lump = SvnLump()
        lump.set_header('Node-kind', 'file')
        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 2)
        self.assertEqual(self.writer.lumps[0].get_header('Revision-number'), '13')
        self.assertEqual(self.writer.lumps[1].get_header('Node-kind'), 'file')
   
    def test_fix_content_length_text(self):
        lump = SvnLump()
        lump.set_header('Node-kind', 'file')
        lump.set_header('Text-content-length', '3')
        fh = StringIO('bla')
        lump.content = ContentTin(fh, 3, 'FAKE-MD5SUM')

        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 1)
        self.assertEqual(self.writer.lumps[0].get_header('Text-content-length'), '3')
        self.assertEqual(self.writer.lumps[0].get_header('Content-length'), '3')

    def test_fix_content_length_prop_no_old(self):
        lump = SvnLump()
        lump.set_header('Node-kind', 'file')
        lump.properties = { 'blub': 'XXX' }

        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 1)
        self.assertEqual(self.writer.lumps[0].get_header('Prop-content-length'), '27')
        self.assertEqual(self.writer.lumps[0].get_header('Content-length'), '27')

    def test_fix_content_length_prop_with_old(self):
        lump = SvnLump()
        lump.set_header('Node-kind', 'file')
        lump.set_header('Prop-content-length', '26')
        lump.set_header('Content-length', '26')
        lump.properties = { 'blub': 'XXX' }

        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 1)
        self.assertEqual(self.writer.lumps[0].get_header('Prop-content-length'), '27')
        self.assertEqual(self.writer.lumps[0].get_header('Content-length'), '27')

    def test_fix_content_length_text_and_prop(self):
        lump = SvnLump()
        lump.set_header('Node-kind', 'file')
        lump.set_header('Text-content-length', '3')
        lump.properties = { 'blub': 'XXX' }
        fh = StringIO('bla')
        lump.content = ContentTin(fh, 3, 'FAKE-MD5SUM')

        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 1)
        self.assertEqual(self.writer.lumps[0].get_header('Text-content-length'), '3')
        self.assertEqual(self.writer.lumps[0].get_header('Prop-content-length'), '27')
        self.assertEqual(self.writer.lumps[0].get_header('Content-length'), '30')

    def test_create_parent_dirs(self):
        self.config.create_parent_dirs = True

        lump = SvnLump()
        lump.set_header('Revision-number', '12')
        self.processor.write_lump(lump)

        self.assertEqual(len(self.writer.lumps), 3)
        self.assertEqual(self.writer.lumps[0].get_header('Revision-number'), '12')
        self.assertEqual(self.writer.lumps[1].get_header('ParentDirectoryGeneratorMockLump'), '1of2')
        self.assertEqual(self.writer.lumps[2].get_header('ParentDirectoryGeneratorMockLump'), '2of2')
