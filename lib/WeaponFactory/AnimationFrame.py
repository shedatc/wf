from pygame import Rect

from .Screen import Screen
from .utils  import log_ex

class AnimationFrame:

    def log(self, msg):
        log_ex(f"Frame '{self.name}': {msg}", category=self.__class__.__name__)

    def __init__(self, name, surface, rect,
                 duration=100, rotated=False, trimmed=False):
        self._duration = duration # ms
        self._rect     = rect
        self._surface  = surface
        self.name      = name

        self.log(f"Surface:   {surface}")
        self.log(f"Rectangle: {rect}")

        assert rotated is False, "Frame rotation is not supported"
        assert trimmed is False, "Frame trim is not supported"

        self._remaining_duration = self._duration

    def reset(self):
        self.log(f"Reset")
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

        self.log(f"Added {t} ms")
        self.log(f"{orig_remaining_duration}→{self._remaining_duration} ms to complete")
        self.log(f"{dt} ms extra")
        return dt

    def is_done(self):
        return self._remaining_duration == 0

    def blit_at(self, position):
        dest_rect        = self._rect.copy()
        dest_rect.center = position
        self.log(f"Blit {self._rect} at {position}")
        Screen.singleton().blit(self._surface, dest_rect,
                                source_rect=self._rect)

