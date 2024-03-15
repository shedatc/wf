from .utils  import log_ex

class Animation:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, name, frames, is_loop=True):
        self.name      = name
        self.frames    = frames
        self.is_loop   = is_loop
        self.last      = len(frames) - 1
        self.current   = 0

    def rewind(self):
        self.current = 0

    def is_done(self):
        return not self.is_loop and self.current == self.last

    def _next_frame(self):
        assert not self.is_done()
        if self.current < self.last:
            self.current += 1
            return True
        elif self.current == self.last and self.is_loop:
            self.current = 0
            return True
        assert 0 <= self.current and self.current < self.last
        return False # No next frame

    def add_time(self, t):
        assert t > 0
        assert not self.is_done()
        while t > 0:
            f = self.frames[self.current]
            t = f.add_time(t)
            if f.is_done():
                if not self._next_frame():
                    return

    def blit_at(self, surface, x, y):
        self.frames[self.current].blit_at(surface, x, y)
