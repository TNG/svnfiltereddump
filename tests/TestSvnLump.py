
from unittest import TestCase

from svnfiltereddump import SvnLump

class SvnLumpTests(TestCase):

    def testSimpleLump(self):
        lump = SvnLump()
        lump.set_header('a_hdr', 'y')
        lump.set_header('c_hdr', 'z')
        lump.set_header('b_hdr', 'x')
        lump.set_header('d_hdr', 'x')
        lump.delete_header('b_hdr')
        lump.properties['prop_a'] = 'bla'
        lump.properties['prop_a'] = 'blub'
        lump.content = 'Something'

        self.assertEqual(lump.get_header_keys(), [ 'a_hdr', 'c_hdr', 'd_hdr' ])
        self.assertEqual(lump.get_header('a_hdr'), 'y')
        self.assertEqual(lump.get_header('c_hdr'), 'z')
        self.assertEqual(lump.get_header('d_hdr'), 'x')
        self.assertTrue(lump.has_header('a_hdr'))
        self.assertFalse(lump.has_header('x_hdr'))
