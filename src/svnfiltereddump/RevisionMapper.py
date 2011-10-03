
from logging import info

class RevisionMapper(object):

    def __init__(self, config):
        self.start_rev = 0
        if config.start_rev:
            self.start_rev = config.start_rev
        self.revision_map = { }
        self.next_free_rev = 0
        self.renumber_revs = config.renumber_revs

    def map_new_output_rev_for_input_rev(self, input_rev):
        if input_rev < self.start_rev:
            raise Exception(
                "Can not map a revsion (%d) below the start-rev (%d)!"
                % ( input_rev, self.start_rev )
            )
        if self.revision_map.has_key(input_rev):
            raise Exception(
                "Revision %d is already mapped!" % ( input_rev )
            )
        
        if self.renumber_revs:
            new_rev = self.next_free_rev
            if input_rev != 0 and new_rev == 0:
                # Only map rev 0 to output rev 0
                new_rev += 1
        else:
            new_rev = input_rev
        self.revision_map[input_rev] = new_rev
        info("    Mapped input revsion input revsion %d to output revsion %d." % ( input_rev, new_rev ) )
        self.next_free_rev = new_rev + 1
        return new_rev

    def get_output_rev_for_input_rev(self, input_rev):
        if input_rev < self.start_rev:
            return self.revision_map[self.start_rev]
        else:
            return self.revision_map[input_rev]
