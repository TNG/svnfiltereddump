
from unittest import TestCase
from StringIO import StringIO
from svnfiltereddump import ContentTin



class ContentTinTests(TestCase):

    def setUp(self):
        self.fh = StringIO("xxxYYYzzz")
        self.out_fh = StringIO()

    def test_simple_tin(self):
        self.fh.read(3)

        with ContentTin(self.fh, 3) as tin:
            tin.empty_to(self.out_fh)

        self.out_fh.seek(0)
        self.assertEqual(self.out_fh.read(), 'YYY')
  
    def test_discard_tin(self):
        with ContentTin(self.fh, 3) as ct:
            pass

        self.assertEqual(self.fh.tell(), 3)


    def test_throws_on_overrun(self):
        fh = StringIO("")
        tin = ContentTin(fh, 3)
        self.assertRaises(Exception, tin.empty_to, self.out_fh)

    def test_only_usable_once(self):
        with ContentTin(self.fh, 4) as tin:
            tin.empty_to(self.out_fh)
            self.assertRaises(Exception, tin.empty_to, self.out_fh)
