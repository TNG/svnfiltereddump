
from logging import info

class LumpPostProcessor(object):
    def __init__(self, config, revision_mapper, writer):
        self.config = config
        self.revision_mapper = revision_mapper
        self.writer = writer
        self.delayed_revision_header = None
        self.parent_dir_lumps_must_be_injected = True
        self.parent_directory_lump_generator = None
        self.last_revision_passed = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self._discard_deplayed_revision_header()
        return False

    def write_lump(self, lump):
        if lump.has_header('Revision-number'):
            self._discard_deplayed_revision_header()
            self.delayed_revision_header = lump
            if self.config.keep_empty_revs:
                self._flush_delayed_revision_header()
            if self.parent_dir_lumps_must_be_injected:
                if self.config.create_parent_dirs:
                    self.parent_directory_lump_generator.write_lumps()
                self.parent_dir_lumps_must_be_injected = False
        else:
            self._flush_delayed_revision_header()
            self._process_lump(lump)

    def _discard_deplayed_revision_header(self):
        if not self.delayed_revision_header:
            return
        info('Dropping empty revision.');
        if self.last_revision_passed:
            mapper = self.revision_mapper
            input_rev = int(self.delayed_revision_header.get_header('Revision-number'))
            output_rev = self.last_revision_passed
            mapper.map_input_rev_to_output_rev(input_rev, output_rev)
        self.delayed_revision_header = None

    def _flush_delayed_revision_header(self):
        if not self.delayed_revision_header:
            return
        mapper = self.revision_mapper
        rev = int(self.delayed_revision_header.get_header('Revision-number'))
        mapper.map_input_rev_to_output_rev(rev, rev)
        self._process_lump(self.delayed_revision_header)
        self.last_revision_passed = rev
        self.delayed_revision_header = None

    def _process_lump(self, lump):
        self._fix_length_fields(lump)
        self._fix_revision_fields(lump)
        self.writer.write_lump(lump)

    def _fix_length_fields(self, lump):
        prop_content_length = self._calculate_prop_content_length(lump)
        if prop_content_length:
            lump.set_header('Prop-content-length', str(prop_content_length))
        elif lump.has_header('Prop-content-length'):
            lump.delete_header('Prop-content-length')

        text_content_length = 0
        if lump.has_header('Text-content-length'):
            text_content_length = int(lump.get_header('Text-content-length'))

        content_length = prop_content_length + text_content_length
        if content_length:
            lump.set_header('Content-length', str(content_length))
        elif lump.has_header('Content-length'):
            lump.delete_header('Content-length')

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

    def _fix_revision_fields(self, lump):
        if lump.has_header('Node-copyfrom-rev'):
            input_revision = int(lump.get_header('Node-copyfrom-rev'))
            mapped_revision = self.revision_mapper.get_output_rev_for_input_rev(input_revision)
            lump.set_header('Node-copyfrom-rev', str(mapped_revision))
