
from unittest import TestCase
from StringIO import StringIO
from svnfiltereddump import ContentTin



class ContentTinTests(TestCase):

    def setUp(self):
        self.fh = StringIO("xxxYYYzzz")
        self.out_fh = StringIO()

    def test_simple_tin(self):
        self.fh.read(3)

        with ContentTin(self.fh, 3, 'MD5SUM') as tin:
            self.assertEqual(tin.md5sum, 'MD5SUM')
            self.assertEqual(tin.size, 3)

            tin.empty_to(self.out_fh)

            self.assertEqual(tin.md5sum, 'MD5SUM')
            self.assertEqual(tin.size, 3)

        self.out_fh.seek(0)
        self.assertEqual(self.out_fh.read(), 'YYY')
  
    def test_discard_tin(self):
        with ContentTin(self.fh, 3, 'MD5SUM') as ct:
            pass

        self.assertEqual(self.fh.tell(), 3)


    def test_throws_on_overrun(self):
        fh = StringIO("")
        tin = ContentTin(fh, 3, 'MD5SUM')
        self.assertRaises(Exception, tin.empty_to, self.out_fh)

    def test_only_usable_once(self):
        with ContentTin(self.fh, 4, 'MD5SUM') as tin:
            tin.empty_to(self.out_fh)
            self.assertRaises(Exception, tin.empty_to, self.out_fh)
