
from os.path import normpath
from SvnLump import SvnLump
from SvnRepository import SvnRepository

class LumpBuilder(object):
    def __init__(self, source_repository):
        self.source_repository = source_repository

    def delete_path(self, path):
        lump = SvnLump()
        lump.set_header('Node-path', normpath(path))
        lump.set_header('Node-action', 'delete')
        return lump

    def add_path_from_source_repository(self, path, rev):
        path = normpath(path)
        repo = self.source_repository
        lump = SvnLump()

        lump.set_header('Node-path', path)

        node_type = repo.get_type_of_path(path, rev)
        if node_type is None:
            raise Exception(
                "Trying to copy %s, revision %d from source repository, but it does not exist!"
                % ( path, rev )
            )
        lump.set_header('Node-kind', node_type)

        lump.set_header('Node-action', 'add')

        if node_type == 'file':
            tin = repo.get_tin_for_file(path, rev)
            lump.content = tin
            lump.set_header('Text-content-length', str(tin.size))
            lump.set_header('Text-content-md5', tin.md5sum)

        lump.properties = repo.get_properties_of_path(path, rev)
        return lump
