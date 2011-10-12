
from logging import info

class LumpPostProcessor(object):
    def __init__(self, config, writer):
        self.config = config
        self.writer = writer
        self.delayed_revision_header = None
        self.parent_dir_lumps_must_be_injected = True
        self.parent_directory_lump_generator = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if self.delayed_revision_header:
            info('Dropping empty revision.');
        return False

    def write_lump(self, lump):
        if lump.has_header('Revision-number'):
            if self.delayed_revision_header:
                info('Dropping empty revision.');
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

    def _flush_delayed_revision_header(self):
        if self.delayed_revision_header:
            self._process_lump(self.delayed_revision_header)
            self.delayed_revision_header = None

    def _process_lump(self, lump):
        self._fix_length_fields(lump)
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

