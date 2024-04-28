from .Screen import Screen
from .utils  import log_ex

class AnimationFrame:

    def log(self, msg):
        log_ex(f"Frame '{self.name}': {msg}", category=self.__class__.__name__)

    def __init__(self, name, surface, rect,
                 duration=100, rotated=False, trimmed=False):
        self._rect    = rect
        self._surface = surface
        self.duration = duration # ms
        self.name     = name

        self.log(f"Animation Frame '{name}':")
        self.log(f"    Duration:  {duration}")
        self.log(f"    Surface:   {surface}")
        self.log(f"    Rectangle: {rect}")

        assert rotated is False, "Frame rotation is not supported"
        assert trimmed is False, "Frame trim is not supported"

    def blit_at(self, position):
        dest_rect        = self._rect.copy()
        dest_rect.center = position
        self.log(f"Blit {self._rect} at {position}")
        Screen.singleton().blit(self._surface, dest_rect.topleft,
                                source_rect=self._rect)
