
from unittest import TestCase
from StringIO import StringIO
from svnfiltereddump import ContentTin



class ContentTinTests(TestCase):

    def test_simple_tin(self):
        fh = StringIO("xxxYYYzzz")
        fh.read(3)
        out_fh = StringIO()

        with ContentTin(fh, 3) as tin:
            tin.empty_to(out_fh)

        out_fh.seek(0)
        self.assertEqual(out_fh.read(), 'YYY')
  
    def test_discard_tin(self):
        fh = StringIO("xxxYYYzzz")
        with ContentTin(fh, 3) as ct:
            pass

        self.assertEqual(fh.tell(), 3)


    def test_throws_on_overrun(self):
        fh = StringIO("")
        tin = ContentTin(fh, 3)
        out_fh = StringIO()
        self.assertRaises(Exception, tin.empty_to, out_fh)

    def test_only_usable_once(self):
        fh = StringIO("asdfasdfasd")
        out_fh = StringIO()
        with ContentTin(fh, 4) as tin:
            tin.empty_to(out_fh)
            self.assertRaises(Exception, tin.empty_to, out_fh)
