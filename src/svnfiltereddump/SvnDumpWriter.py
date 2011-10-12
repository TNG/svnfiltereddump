
from logging import info

class SvnDumpWriter(object):
    def __init__(self, file_handle):
        self.file_handle = file_handle

    def write_lump(self, lump):
        self._write_headers(lump)
        props_written = self._write_properties(lump)
        content_written = self._write_content(lump)
        if props_written or content_written:
            self.file_handle.write("\n") 

    def _write_headers(self, lump):
        fh = self.file_handle
        for header_name in lump.get_header_keys():
            header_value = lump.get_header(header_name)
            fh.write(
                "%s: %s\n"
                % ( header_name, header_value )
            )
        fh.write("\n") 

    def _write_properties(self, lump):
        if not lump.properties:
            return False
        fh = self.file_handle
        for key in sorted(lump.properties.keys()):  # Sorted for easier testing
            value = lump.properties[key]
            fh.write(
                "K %d\n%s\nV %d\n%s\n"
                % ( len(key), key, len(value), value )
            )
        fh.write("PROPS-END\n")
        return True

    def _write_content(self, lump):
        tin = lump.content
        if tin:
            tin.empty_to(self.file_handle)
            self.file_handle.write("\n") 
            return True
        else:
            return False
