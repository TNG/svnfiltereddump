#
# This class is a wrapper around subprocess.Popen
#
# It behaves like a the stdout pipe generated by Popen.
# However it makes a serious efford to do this:
# 1) Forward STDERR of generated process to our STDERR
# 2) Don't get stuck - no matter how much output we get
#    on STDOUT or STDERR
# 3) Raise an Exception if the exit code was not 0
# 4) Raise an Exception if there was data on STDERR
#

from fcntl import fcntl, F_GETFL, F_SETFL
from os import waitpid, O_NONBLOCK
from sys import stderr
from subprocess import Popen, check_call, PIPE, STDOUT
from string import join
from errno import EAGAIN
import re

class CheckedCommandFileHandle(object):

    def __init__(self, args, ignore_patterns=[], error_fh=stderr):
        self.status_ok = True
        self.args = args
        self.ignore_patterns = ignore_patterns
        self.error_fh = error_fh
        self.process = Popen(args, stdout=PIPE, stderr=PIPE)
        self._make_stderr_non_blocking()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if exc_value:
            self._empty_stderr()
            return False
        else:
            self.close()
            return True

    def __iter__(self):
        return self.process.stdout

    def _make_stderr_non_blocking(self):
        file_no = self.process.stderr.fileno()
        bits = O_NONBLOCK | fcntl(file_no, F_GETFL)
        fcntl(file_no, F_SETFL, bits)

    def next(self):
        self._empty_stderr()
        return self.process.stdout.next()

    def readline(self, size=-1):
        self._empty_stderr()
        return self.process.stdout.readline(size)

    def read(self, size=-1):
        self._empty_stderr()
        return self.process.stdout.read(size)

    def _empty_stderr(self):
        try:
            error = self.process.stderr.read()
        except IOError as (errno, strerror):
            if errno == EAGAIN:
                return
            raise
        self._validate_error_output(error)

    def _validate_error_output(self, error):
        if not error:
            return
        if error[-1:] == "\n":
            error = error[:-1]
        error_lines = error.split("\n")
        line_ok = False
        for line in error_lines:
            line_ok = False
            for pattern in self.ignore_patterns:
                if re.search(pattern, line):
                    line_ok = True
                    break
            if not line_ok:
                self.error_fh.write("FAILED LINE: '"+line+"'\n")
                cmd = join(self.args, ' ')
                self.error_fh.write("Output of command '%s' on STDERR:\n%s\n" % ( cmd, error ) )
                raise Exception("Command '%s' wrote to STDERR (see above)!" % ( cmd ))

    def close(self):
        p = self.process
        self._empty_stderr()
        p.stdout.close()
        self._empty_stderr()
        p.stderr.close()
        status = waitpid(p.pid, 0)[1]
        if status:
            raise Exception(
                "Command '%s' exited with status %d"
                % ( join(self.args), status )
            )

