
from os.path import normpath
from copy import copy
from logging import info

from SvnLump import SvnLump
from SvnRepository import SvnRepository


class LumpBuilder(object):
    def __init__(self, config, source_repository, interesting_paths, dump_writer):
        self.config = config
        self.source_repository = source_repository
        self.interesting_paths = interesting_paths
        self.dump_writer = dump_writer

    def delete_path(self, path):
        lump = SvnLump()
        lump.set_header('Node-path', normpath(path))
        lump.set_header('Node-action', 'delete')
        self.dump_writer.write_lump(lump)

    def mkdir(self, path):
        lump = SvnLump()
        lump.set_header('Node-path', normpath(path))
        lump.set_header('Node-kind', 'dir')
        lump.set_header('Node-action', 'add')
        self.dump_writer.write_lump(lump)

    def get_node_from_source(self, kind, path, action, from_path, from_rev):
        assert kind == 'file' or kind == 'dir'
        assert action == 'add' or action =='replace'

        if self._is_obsolete_tag_or_branch_copy(path, from_rev):
            self._handle_obsolete_tag_or_branch(path)
            return

        path = normpath(path)
        repo = self.source_repository
        lump = SvnLump()

        lump.set_header('Node-path', path)
        lump.set_header('Node-kind', kind)
        lump.set_header('Node-action', action)

        if kind == 'file':
            tin = repo.get_tin_for_file(from_path, from_rev)
            lump.content = tin
            lump.set_header('Text-content-length', str(tin.size))
            lump.set_header('Text-content-md5', tin.md5sum)

        lump.properties = repo.get_properties_of_path(from_path, from_rev)
        self.dump_writer.write_lump(lump)

    def _is_obsolete_tag_or_branch_copy(self, path, from_rev):
        if not self.config.start_rev:
            return False
        if not self.config.drop_old_tags_and_branches:
            return False
        return self.config.is_path_tag_or_branch(path)

    def _handle_obsolete_tag_or_branch(self, path):
        info('Excluding obsolete tag/branch: ' + path)
        self.interesting_paths.mark_path_as_boring(path)

    def get_path_from_target(self, kind, path, action, from_path, from_rev):
        assert kind == 'file' or kind =='dir'
        assert action == 'add' or action =='replace'

        lump = SvnLump()
        lump.set_header('Node-path', path)
        lump.set_header('Node-kind', kind)
        lump.set_header('Node-action', action)
        lump.set_header('Node-copyfrom-path', from_path)
        lump.set_header('Node-copyfrom-rev', str(from_rev))
        self.dump_writer.write_lump(lump)

    def change_lump_from_add_or_replace_lump(self, sample_lump):
        lump = copy(sample_lump)
        lump.set_header('Node-action', 'change')
        for header_name in [
            'Node-kind', 'Node-copyfrom-path', 'Node-copyfrom-rev',
            'Text-copy-source-md5', 'Text-copy-source-sha1'
        ]:
            if lump.has_header(header_name):
                lump.delete_header(header_name)
        self.dump_writer.write_lump(lump)

    def revision_header(self, rev, log_message=None):
        lump = SvnLump()
        lump.set_header('Revision-number', str(rev))
        rev_info = self.source_repository.get_revision_info(rev)
        if log_message:
            new_log_message = log_message
        else:
            new_log_message = rev_info.log_message
        lump.properties = {
            'svn:author': rev_info.author,
            'svn:date': rev_info.date,
            'svn:log': new_log_message
        }
        self.dump_writer.write_lump(lump)

    def dump_header_lumps(self):
        lump = SvnLump()
        lump.set_header('SVN-fs-dump-format-version', '2')
        self.dump_writer.write_lump(lump)

        lump = SvnLump()
        lump.set_header('UUID', str(self.source_repository.get_uuid()))
        self.dump_writer.write_lump(lump)

    def pass_lump(self, lump):
        self.dump_writer.write_lump(lump)

    def get_recursively_from_source(self, kind, path, action, from_path, from_rev):
        assert kind == 'file' or kind =='dir'
        assert action == 'add' or action =='replace'

        if self._is_obsolete_tag_or_branch_copy(path, from_rev):
            self._handle_obsolete_tag_or_branch(path)
            return
        if kind == 'file':
            self.get_node_from_source(kind, path, action, from_path, from_rev)
        else:
            if action == 'replace':
                self.delete_path(path)
            self._add_tree_from_source(path, from_path, from_rev)

    def _add_tree_from_source(self, path, from_path, from_rev):
        if path[-1:] != '/' and len(path)>0:
            path += '/'
        if from_path[-1:] != '/':
            from_path += '/'
        with self.source_repository.get_tree_handle_for_path(from_path, from_rev) as tree_handle:
            for from_sub_path in tree_handle:
                if from_sub_path[-1:] == '/':
                    kind = 'dir'
                    from_sub_path = from_sub_path[:-1]
                else:
                    kind = 'file'
                sub_path = path + from_sub_path[len(from_path):]
                if sub_path == '':
                    continue
                if self.interesting_paths.is_interesting(sub_path):
                    self.get_node_from_source(kind, sub_path, 'add', from_sub_path, from_rev)
