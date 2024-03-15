from pygame import Rect

from .utils import log_ex

class AnimationFrame:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

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
        AnimationFrame.log("Reset")
        self._remaining_duration = self._duration

    # Add time to the frame. If adding more time than necessary to finish it,
    # return time remaining, i.e., this time is left to the next frame.
    def add_time(self, t):
        assert self._remaining_duration > 0
        orig_remaining_duration = self._remaining_duration
        if t <= self._remaining_duration:
            dt                        = 0
            self._remaining_duration -= t
        else:
            assert t > self._remaining_duration
            dt                       = t - self._remaining_duration
            self._remaining_duration = 0

        AnimationFrame.log(f"Added {t} ms")
        AnimationFrame.log(f"{orig_remaining_duration}→{self._remaining_duration} ms to complete")
        AnimationFrame.log(f"{dt} ms extra")
        return dt

    def is_done(self):
        return self._remaining_duration == 0

    def blit_at(self, surface, x, y):
        surface.blit(self._surface,                                   # source
                     (x - self._width // 2, y - self._height // 2),   # dest
                     area=Rect((self._x, self._y), (self._width, self._height)))

