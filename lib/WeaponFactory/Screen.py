from pygame         import FULLSCREEN, SCALED
from pygame.display import set_caption, set_mode
from pygame.draw    import rect as draw_rect

from .const import COLOR_BLACK, DEBUG_BLIT
from .utils import log_ex, sz

class Screen:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, size, caption=None):
        self._surface = set_mode(size, FULLSCREEN|SCALED)
        rect          = self._surface.get_rect()
        self.size     = rect.size
        if caption is not None:
            set_caption(caption)
        Screen.log(f"Screen:")
        Screen.log(f"    Size:    {sz(rect.size)} ({sz(size)} requested)")
        Screen.log(f"    Caption: {caption}")

        Screen._singleton = self

    def reset(self):
        self._surface.fill(COLOR_BLACK)

    # Dest is a (x, y) tuple.
    def blit(self, source_surface, dest, source_rect=None):
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit from {source_surface} to screen@{dest}")
            else:
                Screen.log(f"Blit from {source_rect}@{source_surface} to screen@{dest}")
        self._surface.blit(source_surface, dest, area=source_rect)

    def draw_rect(self, color, rect, width=0):
        draw_rect(self._surface, color, rect, width=width)
