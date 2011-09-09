class NonOut(object):
    def write(self, what):
        pass

class ContentTin:

    chunk_size = 1024**2

    def __init__(self, fh, size):
        self.fh = fh
        self.remaining_bytes = size
        self.used = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if not exc_type and not self.used:
            self.empty_to()
   
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
