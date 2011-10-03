
import re
from StringIO import StringIO
from unittest import TestCase

from svnfiltereddump import CheckedCommandFileHandle


class TestCheckedCommandFileHandle(TestCase):

    def setUp(self):
        self.stderr_mock = StringIO()

    def get_output_lines_of_command(self, args, ignore_patterns = [ ]):
        lines = [ ]
        with CheckedCommandFileHandle(args, ignore_patterns, self.stderr_mock) as fh:
            for line in fh:
                lines.append(line)
        return lines

    def test_ok(self):
        args = [ 'sh', '-c', 'echo Bla; echo Blub' ]

        lines = self.get_output_lines_of_command(args)
        self.assertEqual(lines, [ "Bla\n", "Blub\n" ])

        with CheckedCommandFileHandle(args, self.stderr_mock) as fh:
            output = fh.read()
        self.assertEqual(output, "Bla\nBlub\n")

        lines = [ ]
        with CheckedCommandFileHandle(args, self.stderr_mock) as fh:
            line = fh.readline()
            while line:
                lines.append(line)
                line = fh.readline()
        self.assertEqual(lines, [ "Bla\n", "Blub\n" ] )
        self.stderr_mock.seek(0)
        self.assertEqual(self.stderr_mock.read(), '')

    def test_stderr_bad(self):
        args = [ 'sh', '-c', 'echo Bla; echo Blub >&2' ]
       
        self.assertRaises(Exception, self.get_output_lines_of_command, args)
        self.stderr_mock.seek(0)
        out = self.stderr_mock.read()
        self.assertTrue(re.search("Output of command 'sh -c echo Bla; echo Blub >&2' on STDERR:\nBlub\n", out))

    def test_stderr_bad_with_ignore(self):
        args = [ 'sh', '-c', 'echo Bla; echo Blub >&2' ]
        ignore_patterns = [ 'foo', '^Bla', 'bar' ]
       
        self.assertRaises(Exception, self.get_output_lines_of_command, args, ignore_patterns)
        self.stderr_mock.seek(0)
        out = self.stderr_mock.read()
        self.assertTrue(re.search("Output of command 'sh -c echo Bla; echo Blub >&2' on STDERR:\nBlub\n", out))

    def test_stderr_good(self):
        args = [ 'sh', '-c', 'echo Bla something >&2' ]
        ignore_patterns = [ 'foo', '^Bla', 'bar' ]
      
        self.get_output_lines_of_command(args, ignore_patterns) 
        self.stderr_mock.seek(0)
        self.assertEqual(self.stderr_mock.read(), '')

    def test_error_exit(self):
        args = [ 'sh', '-c', 'echo Bla; echo Blub; exit 1' ]

        self.assertRaises(Exception, self.get_output_lines_of_command, args)
