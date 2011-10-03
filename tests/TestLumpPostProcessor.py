
from unittest import TestCase
from StringIO import StringIO

from svnfiltereddump import Config, LumpPostProcessor, ContentTin, SvnLump

from DumpWriterMock import DumpWriterMock

class RevisionMapperMock(object):
    def __init__(self):
        self.mapped_revs = [ ]

    def map_new_output_rev_for_input_rev(self, input_rev):
        self.mapped_revs.append(input_rev)
        return input_rev + 3

    def get_output_rev_for_input_rev(self, input_rev):
        return input_rev + 3

class TestLumpPostProcessor(TestCase):
    def setUp(self):
        self.config = Config( [ '/dummy' ] )
        self.rev_mapper = RevisionMapperMock()
        self.writer = DumpWriterMock(self)
        self.processor = LumpPostProcessor(self.config, self.rev_mapper, self.writer)

    def test_dont_drop_empty_revs(self):
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
        self.assertEqual(self.writer.lumps[0].get_header('Revision-number'), '15')
        self.assertEqual(self.writer.lumps[1].get_header('Revision-number'), '16')
        self.assertEqual(self.writer.lumps[2].get_header('Node-kind'), 'file')

    def test_drop_empty_revs(self):
        self.config.drop_empty_revs = True

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
        self.assertEqual(self.writer.lumps[0].get_header('Revision-number'), '16')
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

    def test_map_revisions(self):
        lump = SvnLump()
        lump.set_header('Revision-number', '12')

        self.processor.write_lump(lump)
        self.assertEqual(self.rev_mapper.mapped_revs, [ 12 ])

        lump = SvnLump()
        lump.set_header('Node-copyfrom-rev', '12')

        self.processor.write_lump(lump)
        self.assertEqual(self.writer.lumps[1].get_header('Node-copyfrom-rev'), '15')

