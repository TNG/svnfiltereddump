
#
# Purpose:
#
# When we process the output of "svnadmin dump" we want
# to 'stream' some parts ('content') of it via limited
# size buffer to the output. Other content we just want
# to discard.
#
# Regardless if we stream or discard: The file handle of
# the input file handle must be at the right position just
# after the content once we are done with it.
#
# That logic is encapsuled here. Once we identified a
# piece of 'content' we create a ContentTin with it.
#

class NonOut(object):
    def write(self, what):
        pass

class ContentTin:

    chunk_size = 1024**2

    def __init__(self, fh, size, md5sum):
        self.fh = fh
        self.size = size
        self.remaining_bytes = size
        self.md5sum = md5sum
        self.used = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if not exc_type and not self.used:
            self.empty_to()
        return False
   
    def empty_to(self, out_fh = NonOut()):
        if self.used:
            raise Exception("ContentTins can only be used once")
        while self.remaining_bytes > 0:
            chunk = min(self.chunk_size, self.remaining_bytes)
            input_chunk = self.fh.read(chunk)
            if input_chunk == "":
                raise Exception("read beyond end of file")
            self.remaining_bytes -= len(input_chunk)
            out_fh.write(input_chunk)
        self.used = True

    def discard(self):
        if not self.used:
            self.empty_to()
