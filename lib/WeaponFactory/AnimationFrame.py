from pygame import Rect

class AnimationFrame:

    def __init__(self, surface, x, y, width, height,
                 duration=100, rotated=False, trimmed=False):
        self._surface  = surface
        self._x        = x
        self._y        = y
        self._width    = width
        self._height   = height
        self._duration = duration # ms

        assert rotated is False, "Frame rotation is not supported"
        assert trimmed is False, "Frame trim is not supported"

        self._remaining_duration = self._duration

    def reset(self):
        self._remaining_duration = self._duration

    # Add time to the frame. If adding more time than necessary to finish it,
    # return time remaining, i.e., the time that was not consumed.
    def add_time(self, t):
        if t <= self._remaining_duration:
            self._remaining_duration -= t
            return 0
        else:
            self._remaining_duration = 0
            return t - self._remaining_duration

    def is_done(self):
        return self._remaining_duration == 0

    def blit_at(self, surface, x, y):
        surface.blit(self._surface,                                   # source
                     (x - self._width // 2, y - self._height // 2),   # dest
                     area=Rect((self._x, self._y), (self._width, self._height)))

