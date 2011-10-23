
from logging import debug

class RevisionMapper(object):

    def __init__(self, config):
        self.start_rev = 0
        if config.start_rev:
            self.start_rev = config.start_rev
        self.revision_map = { }
        self.next_free_rev = 0

    def map_input_rev_to_output_rev(self, input_rev, output_rev):
        if input_rev < self.start_rev:
            raise Exception(
                "Can not map a revsion (%d) below the start-rev (%d)!"
                % ( input_rev, self.start_rev )
            )
        if self.revision_map.has_key(input_rev):
            raise Exception(
                "Revision %d is already mapped!" % ( input_rev )
            )
        
        self.revision_map[input_rev] = output_rev
        debug("    Mapped input revsion input revsion %d to output revsion %d." % ( input_rev, output_rev ) )

    def get_output_rev_for_input_rev(self, input_rev):
        if input_rev < self.start_rev:
            return self.revision_map[self.start_rev]
        else:
            return self.revision_map[input_rev]
