
from re import match
from SvnLump import SvnLump
from ContentTin import ContentTin
from string import join

class SvnDumpReader(object):

    def __init__(self, file_handle):
        self.file_handle = file_handle
        self.current_lump = None

    def read_lump(self):
        self._finish_last_lump()
        self.current_lump = SvnLump()
        self._read_headers()
        if not self.current_lump.get_header_keys():
            return None
        self._read_properties()
        self._create_content_tin()
        return self.current_lump

    def _finish_last_lump(self):
        # Ensure that ContentTin of last lump gets depleted
        if self.current_lump and self.current_lump.content:
            self.current_lump.content.discard()

    def _read_headers(self):
        fh = self.file_handle
        header_count = 0

        while True:
            line = fh.readline()
            if not line:
                if header_count > 0:
                    raise Exception("Found End of file before end of headers!")
                return
            if line == "\n":
                if header_count > 0:
                    return
            else:
                m = match("(.+): (.*)$", line)
                if not m:
                    raise Exception("Found broken header line:\n" + line)
                self.current_lump.set_header(m.group(1), m.group(2))
                header_count += 1

    def _read_properties(self):
        lump = self.current_lump
        if not lump.has_header('Prop-content-length'):
            return
        expected_length = int(lump.get_header('Prop-content-length'))
        actual_length = 0

        while True:
            ( key, key_length ) = self._read_prop_key_and_length()
            actual_length += key_length
            if key is None:
                break;
            ( value, value_length ) = self._read_prop_value_and_length()
            actual_length += value_length
            lump.properties[key] = value
        if actual_length != expected_length:
            raise Exception(
                "PROPS section should be %d bytes long but was %d!"
                % ( expected_length, actual_length )
            )

    def _read_prop_key_and_length(self):
        fh = self.file_handle
        line = fh.readline()
        length = len(line)
        if line == 'PROPS-END\n':
            return ( None, length )
        if not line.startswith('K '):
            raise Exception("Needed key size line (K <number>) but got:\n" + line)
        size = int(line[2:-1])
        ( key, key_length ) = self._read_field_of_given_size_and_length(size)
        length += key_length
        return ( key, length )
        
    def _read_prop_value_and_length(self):
        fh = self.file_handle
        line = fh.readline()
        length = len(line)
        if not line.startswith('V '):
            raise Exception("Needed value size line (V <number>) but got:\n" + line)
        size = int(line[2:-1])
        ( value, value_length ) = self._read_field_of_given_size_and_length(size)
        length += value_length
        return ( value, length )

    def _read_field_of_given_size_and_length(self, size):
        lines = [ ]
        length = 0
        while True:
            line = self.file_handle.readline()
            if not line:
                raise Exception("Reached end-of-file while reading field!")
            lines.append(line)
            length += len(line)
            if length == size+1:
                return ( join(lines, '')[0:-1], length )
            elif length > size+1:
                raise Exception("Field length did not match expected size!")

    def _create_content_tin(self):
        lump = self.current_lump
        if not lump.has_header('Text-content-length'):
            return
        size = int(lump.get_header('Text-content-length'))
        md5sum = lump.get_header('Text-content-md5')
        lump.content = ContentTin(self.file_handle, size, md5sum)
