
import tempfile
import shutil
import os
import sys
import re
from subprocess import Popen, check_call, PIPE, STDOUT
from string import join;

STATE_SEEN_NOTHING = 0
STATE_WANT_REVISION = 1
STATE_WANT_EMPTY_LINE = 2
STATE_READING_COMMIT_COMMENT = 3

SVN_LOG_SEPARATOR = '------------------------------------------------------------------------'

def chomp(x):
    if x[-1:] == "\n":
        return x[:-1]
    else:
        return x

def get_output_of_command(args):
    process = Popen(args, stdout=PIPE, stderr=PIPE )
    output = chomp(process.stdout.read())
    process.stdout.close()
    error = process.stderr.read()
    process.stderr.close()
    status = os.waitpid(process.pid, 0)[1]
    if status != 0:
        cmd_str = join(args, ' ')
        raise Exception("Command '%s' failed with status %d:\n%s" % ( cmd_str, status, error ) )
    return output


class TestEnvironment:
    def __init__(self):
        self.work_dir = tempfile.mkdtemp()
        self.tmp_index = 0
        self.source_repo_path = self.work_dir + '/source_repo'
        self.source_repo_url = 'file://' + self.source_repo_path
        self.source_repo_working_copy = self.work_dir + '/source_wc'
        self.target_repo_path = self.work_dir + '/target_repo'
        self.target_repo_url = 'file://' + self.target_repo_path
        self.dev_null = open('/dev/null', 'w')
       
        check_call( [ 'svnadmin', 'create',  self.source_repo_path ] )
        check_call( [ 'svnadmin', 'create',  self.target_repo_path ] )
        check_call( [ 'svn', 'co', self.source_repo_url, self.source_repo_working_copy ], stdout=self.dev_null )

        os.putenv('LANG', 'en_US.utf8')
        lib_dirs = sys.path
        lib_dirs.append(
            os.path.join(os.path.dirname(__file__), '../src')
        )
        os.putenv('PYTHONPATH', join(lib_dirs, ':'))

    def destroy(self):
        shutil.rmtree(self.work_dir)
        self = None

    def mkdir(self, name):
        os.chdir(self.source_repo_working_copy)
        check_call( [ 'svn', 'mkdir', '--parents', name ], stdout=self.dev_null)

    def mkdir_target(self, name):
        url = self.target_repo_url + '/' + name
        check_call( [ 'svn', 'mkdir', '--parents', '-m', 'mkdir', url ], stdout=self.dev_null)

    def add_file(self, name, content):
        self.change_file(name, content)
        check_call( [ 'svn', 'add', name ], stdout=self.dev_null)

    def copy_file(self, source, target):
        check_call( [ 'svn', 'copy', source, target ], stdout=self.dev_null)

    def rm_file(self, name):
        check_call( [ 'svn', 'rm', name ], stdout=self.dev_null)

    def propset(self, path, key, value):
        os.chdir(self.source_repo_working_copy)
        check_call( [ 'svn', 'propset', key, value, path], stdout=self.dev_null)

    def change_file(self, name, content):
        os.chdir(self.source_repo_working_copy)
        fh = open(name, 'w')
        fh.write(content)
        fh.close()

    def commit(self, comment):
        os.chdir(self.source_repo_working_copy)
        check_call( [ 'svn', 'commit', '-m', comment ], stdout=self.dev_null )

    def filter_repo(self, parameters):
        os.chdir(self.work_dir)

        cmd_path = os.path.join(os.path.dirname(__file__), '../src/bin/svnfiltereddump')
        process = Popen(
            'svnadmin dump ' + self.source_repo_path + ' 2>/dev/null'
            + ' | ' + cmd_path + ' ' + join(parameters, ' ')
            + ' | svnadmin load --ignore-uuid ' + self.target_repo_path + ' 2>/dev/null',
            shell=True, stdout=self.dev_null, stderr=PIPE
        )
        output = process.stderr.read()
        status = os.waitpid(process.pid, 0)[1]
        if status == 0:
            return None
        else:
            return output

    def is_existing_in_rev(self, path, rev):
        url = '%s/%s@%d' % ( self.target_repo_url, path, rev )
        process = Popen( [ 'svn', 'ls', url ], stdout=PIPE, stderr=STDOUT )
        output = process.stdout.read()
        process.stdout.close()
        status = os.waitpid(process.pid, 0)[1]
        if status == 0:
            return True
        elif re.search('non-existent in that revision', output) is not None:
            return False
        else:
            raise Exception(
                "svn ls on path '%s' in revision %d returned unexpeted result:\n%s" %
                ( path, rev, output )
            )

    def get_file_content_in_rev(self, path, rev):
        url = '%s/%s@%d' % ( self.target_repo_url, path, rev )
        return get_output_of_command( [ 'svn', 'cat', url ] )

    def get_log_of_file_in_rev(self, path, rev):
        url = '%s/%s@%d' % ( self.target_repo_url, path, rev )
        process = Popen( [ 'svn', 'log', url ], stdout=PIPE, stderr=PIPE)
        state = STATE_SEEN_NOTHING
        logs_list = [ ]
        revision = None
        comment_lines = [ ]
        line_nr = 0
        error_prefix = "Error processing svn log for path '%s', revision %d," % ( path, rev )
        for line in  process.stdout:
            line_nr += 1
            line = chomp(line)
            if state == STATE_SEEN_NOTHING:
                if line != SVN_LOG_SEPARATOR:
                    raise Exception("%s line %d: No separtor at start of output:\n%s" % ( error_prefix, line_nr, line ) )
                state = STATE_WANT_REVISION
            elif state == STATE_READING_COMMIT_COMMENT:
                if line == SVN_LOG_SEPARATOR:
                    logs_list.append( [ revision, join(comment_lines, "\n") ])
                    state = STATE_WANT_REVISION
                    revision = None
                    comment_lines = [ ]
                else:
                    comment_lines.append(line)
            elif state == STATE_WANT_REVISION:
                m = re.match('r(\d+)\s*\|', line)
                if not m:
                    raise Exception("%s line %d: No revision after a separator line:\n%s" % ( error_prefix, line_nr, line ) )
                revision = int(m.group(1))
                state = STATE_WANT_EMPTY_LINE
            elif state == STATE_WANT_EMPTY_LINE:
                if line != '':
                   raise Exception("%s line %d: Expected empty line before commit comment\ns" % ( error_prefix, line_nr, line ) )
                state = STATE_READING_COMMIT_COMMENT
            else:
                raise Exception("%s line %d: Internal error - unknown state %d" % ( error_prefix, line_nr, state ) )
        process.stdout.close()
        error = process.stderr.read()
        process.stderr.close()
        status = os.waitpid(process.pid, 0)[1]
        if status == 0:
            return ( logs_list, None )
        else:
            return ( logs_list, error )

    def get_property_in_rev(self, path, rev, key):
        url = '%s/%s@%d' % ( self.target_repo_url, path, rev )
        output = get_output_of_command([ 'svn', 'propget', key, url ])
        return chomp(output)

    def get_log_of_revision(self, rev):
        output = get_output_of_command( [ 'svnlook', 'log', '-r', str(rev), self.target_repo_path ] )
        return chomp(output)

    def create_tmp_file(self, content):
        name = self.work_dir + '/tmp_file.' + str(self.tmp_index)
        fh = open(name, 'w')
        fh.write(content)
        fh.close()
        return name

