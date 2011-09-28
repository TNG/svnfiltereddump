
from copy import copy
from StringIO import StringIO

class DumpWriterMock(object):
    def __init__(self, test_case):
        self.lumps = [ ]
        self.test_case = test_case

    def write_lump(self, lump):
        new_lump = copy(lump)
        if lump.content:
            fh = StringIO()
            lump.content.empty_to(fh)
            fh.seek(0)
            new_lump.content = fh.read()    # Hack Part 1
        self.lumps.append(new_lump)

    def check_content_tin_of_lump_nr(self, nr, expected_content):
        self.test_case.assertEqual(self.lumps[nr].content, expected_content) # Hack Part 2

