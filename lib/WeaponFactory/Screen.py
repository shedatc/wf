from math           import radians
from pygame         import FULLSCREEN, Rect, SCALED
from pygame.display import set_caption, set_mode
from pygame.draw    import arc  as draw_arc
from pygame.draw    import line as draw_line
from pygame.draw    import rect as draw_rect
from pygame.font    import Font
from pygame.math    import Vector2

from .Camera import Camera
from .Config import Config
from .colors import COLOR_BLACK, COLOR_GREEN
from .debug  import DEBUG_BLIT
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

        self.surface = set_mode(size, FULLSCREEN|SCALED)
        rect         = self.surface.get_rect()
        self.size    = rect.size
        if caption is not None:
            set_caption(caption)
        self._font = Font(None, 15)
        Screen.log(f"Screen:")
        Screen.log(f"    Size:    {sz(rect.size)} ({sz(size)} requested)")
        Screen.log(f"    Caption: {caption}")

        Screen._singleton = self

    def reset(self):
        self.surface.fill(COLOR_BLACK)

    def screen_blit(self, source_surface, screen_point, source_rect=None):
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit {source_surface} to screen at {screen_point}")
            else:
                Screen.log(f"Blit {source_rect} from {source_surface} to screen at {screen_point}")
        self.surface.blit(source_surface, screen_point, area=source_rect)

    def blit(self, source_surface, world_point, source_rect=None):
        screen_point = Camera.singleton().screen_point(world_point)
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit {source_surface} to screen" \
                           + f" at {world_point} → {screen_point}")
            else:
                Screen.log(f"Blit {source_rect} from {source_surface} to screen" \
                           + f" at {world_point} → {screen_point}")
        self.surface.blit(source_surface, screen_point, area=source_rect)

    def screen_draw_rect(self, screen_rect, color=COLOR_BLACK, width=0):
        draw_rect(self.surface, color, screen_rect, width=width)

    def draw_rect(self, world_rect, color=COLOR_BLACK, width=0):
        screen_rect        = world_rect.copy()
        screen_rect.center = Camera.singleton().screen_point(world_rect.center),
        draw_rect(self.surface, color, screen_rect, width=width)

    def screen_text(self, text, screen_point,
                    color=COLOR_GREEN, bgcolor=COLOR_BLACK):
        text_surf = self._font.render(text,
                                      True,            # antialias
                                      color,
                                      bgcolor)
        self.screen_blit(text_surf, screen_point)

    def text(self, text, world_point,
             color=COLOR_GREEN, bgcolor=COLOR_BLACK):
        screen_point = Camera.singleton().screen_point(world_point),
        self.screen_text(text, screen_point, color=color, bgcolor=bgcolor)

    def draw_point(self, world_point, name=None, color=COLOR_BLACK, stats=False, width=1):
        rect = Rect((0, 0), (width, width))
        rect.center = world_point
        self.draw_rect(rect, color=color, width=width)
        (tx, ty) = rect.bottomright
        tx += 10
        if name is None:
            return
        if stats:
            self.text(f"{name}: {world_point}", (tx, ty), color=color)
        else:
            self.text(f"{name}", (tx, ty), color=color)

    def draw_line(self, world_start, world_end,
                  color=COLOR_BLACK, width=1):
        camera       = Camera.singleton()
        screen_start = camera.screen_point(world_start)
        screen_end   = camera.screen_point(world_end)
        draw_line(self.surface, color, screen_start, screen_end, width)

    def draw_vector(self, world_point, vector,
                    name=None, color=COLOR_BLACK, width=1, stats=False):
        if type(world_point) is Vector2:
            (px, py) = world_point.xy
        else:
            (px, py) = world_point
        if type(vector) is Vector2:
            (vx, vy) = vector.xy
        else:
            (vx, vy) = vector
        self.draw_line(world_point, (px + vx, py + vy), color=color, width=width)
        rect = Rect((0, 0), (5, 5))
        rect.center = (px + vx, py + vy)
        self.draw_rect(rect, color=color)
        if name is None:
            return
        (tx, ty) = rect.bottomright
        tx += 10
        if stats:
            self.text(f"{name}: {vector.xy}",             (tx, ty),      color=color)
            self.text(f"     len: {vector.length():.2f}", (tx, ty + 10), color=color)
        else:
            self.text(name, (tx, ty), color=color)

    def draw_arc(self, rect, start_angle, stop_angle, color=COLOR_BLACK, width=1):
        screen_rect = Camera.singleton().screen_rect(rect)
        draw_arc(self.surface, color, screen_rect, radians(start_angle), radians(stop_angle),
                 width)
