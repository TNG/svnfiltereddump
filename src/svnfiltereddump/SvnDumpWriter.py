
class _HeaderFixer(object):
    def __init__(self, lump, revision_mapper):
        self.prop_content_length = self._calculate_prop_content_length(lump)
        self.content_length = self.prop_content_length
        if lump.has_header('Text-content-length'):
            assert lump.content is not None
            self.content_length += int(lump.get_header('Text-content-length'))
        else:
            assert lump.content is None
        self.revision_mapper = revision_mapper

    def write_fixed_headers(self, lump, file_handle):
        for header_name in lump.get_header_keys():
            raw_header_value = lump.get_header(header_name)
            cooked_header_value = self._get_cooked_value_of_header(header_name, raw_header_value)
            file_handle.write(
                "%s: %s\n"
                % ( header_name, cooked_header_value )
            )

        if self.prop_content_length and  not lump.has_header('Prop-content-length'):
            file_handle.write("Prop-content-length: %d\n" % (  self.prop_content_length ))
        if self.content_length  and  not lump.has_header('Content-length'):
            file_handle.write("Content-length: %d\n" % ( self.content_length ))

    def _calculate_prop_content_length(self, lump):
        if not lump.properties:
            return 0
        sum_so_far = 0
        for key in lump.properties.keys():
            key_length = len(key)
            value_length = len(lump.properties[key])
            sum_so_far += (
                3 + len(str(key_length))        # K 4\n
                + key_length + 1                # blub\n
                + 3 + len(str(value_length))    # V 3\n
                + value_length + 1              # xxx\n
            )
        sum_so_far += 10                        # PROPS-END\n
        return sum_so_far

    def _get_cooked_value_of_header(self, header_name, raw_header_value):
        if header_name == 'Revision-number':
            input_revision = int(raw_header_value)
            mapped_revision = self.revision_mapper.map_output_rev_for_input_rev(input_revision)
            return str(mapped_revision)
        elif header_name == 'Node-copyfrom-rev':
            input_revision = int(raw_header_value)
            mapped_revision = self.revision_mapper.get_output_rev_for_input_rev(input_revision)
            return str(mapped_revision)
        elif header_name == 'Prop-content-length':
            return str(self.prop_content_length)
        elif header_name == 'Content-length':
            return str(self.content_length)
        else:
            return raw_header_value
       
class SvnDumpWriter(object):
    def __init__(self, revision_mapper, file_handle):
        self.revision_mapper = revision_mapper
        self.file_handle = file_handle

    def write_lump(self, lump):
        self._write_fixed_headers(lump)
        props_written = self._write_properties(lump)
        content_written = self._write_content(lump)
        if props_written or content_written:
            self.file_handle.write("\n") 

    def _write_fixed_headers(self, lump):
        fixer = _HeaderFixer(lump, self.revision_mapper)
        fixer.write_fixed_headers(lump, self.file_handle)
        self.file_handle.write("\n") 

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
