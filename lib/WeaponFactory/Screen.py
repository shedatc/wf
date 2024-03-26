from pygame         import FULLSCREEN, SCALED
from pygame.display import set_caption, set_mode
from pygame.draw    import rect as draw_rect
from pygame.font    import Font

from .Camera import Camera
from .Config import Config
from .const  import COLOR_BLACK, COLOR_GREEN, DEBUG_BLIT
from .utils  import log_ex, sz

class Screen:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        config  = Config.singleton().load("screen.json")
        size    = (config["width"], config["height"])
        caption = config["caption"]

        self._surface = set_mode(size, FULLSCREEN|SCALED)
        rect          = self._surface.get_rect()
        self.size     = rect.size
        if caption is not None:
            set_caption(caption)
        self._font = Font(None, 15)
        Screen.log(f"Screen:")
        Screen.log(f"    Size:    {sz(rect.size)} ({sz(size)} requested)")
        Screen.log(f"    Caption: {caption}")

        Screen._singleton = self

    def reset(self):
        self._surface.fill(COLOR_BLACK)

    def screen_blit(self, source_surface, screen_point, source_rect=None):
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit {source_surface} to screen at {screen_point}")
            else:
                Screen.log(f"Blit {source_rect} from {source_surface} to screen at {screen_point}")
        self._surface.blit(source_surface, screen_point, area=source_rect)

    def blit(self, source_surface, world_point, source_rect=None):
        screen_point = Camera.singleton().screen_point(world_point)
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit {source_surface} to screen" \
                           + f" at {world_point} → {screen_point}")
            else:
                Screen.log(f"Blit {source_rect} from {source_surface} to screen" \
                           + f" at {world_point} → {screen_point}")
        self._surface.blit(source_surface, screen_point, area=source_rect)

    def draw_rect(self, color, rect, width=0):
        draw_rect(self._surface, color, rect, width=width)

    def text(self, text, screen_point):
        text_surf = self._font.render(text,
                                      True,            # antialias
                                      COLOR_GREEN,     # color
                                      COLOR_BLACK)     # background
        self.screen_blit(text_surf, screen_point)
