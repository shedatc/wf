from .utils import log_ex

class Animation:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, name, frames, is_loop=True):
        self.name           = name
        self.is_loop        = is_loop
        self._frames        = frames
        self._index_last    = len(frames) - 1
        self._index_current = 0
        self._current       = frames[0]

    def rewind(self):
        Animation.log("Rewinding")
        for f in self._frames:
            Animation.log(f"Reset frame {self._index_current}/{self._index_last}")
            f.reset()
        self._index_current = 0
        Animation.log(f"Rewinding done, now at frame {self._index_current}/{self._index_last}")

    def is_done(self):
        return self._index_current > self._index_last and not self.is_loop

    def _next_frame(self):
        assert not self.is_done()
        self._index_current += 1
        if self._index_current > self._index_last and self.is_loop:
            self.rewind()
        Animation.log(f"Now at frame {self._index_current}/{self._index_last}")

    def add_time(self, t):
        assert t > 0
        assert not self.is_done()
        while t > 0 and not self.is_done():
            Animation.log(f"Adding {t} ms to frame {self._index_current}/{self._index_last}")
            f = self._frames[self._index_current]
            t = f.add_time(t)
            if f.is_done():
                self._next_frame()
        Animation.log(f"Done")

    def blit_at(self, position):
        self._frames[self._index_current].blit_at(position)
