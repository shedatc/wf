from pygame.mouse import get_pos, set_pos, set_visible

from .Camera import Camera
from .Screen import Screen
from .utils  import log_ex

class Mouse:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    @classmethod
    def set_visible(cls, show):
        Mouse.log(f"Set visibility: {show}")
        set_visible(show)

    # Mouse position in screen coordinates.
    @classmethod
    def screen_point(cls):
        return get_pos()

    # Mouse position in world coordinates.
    @classmethod
    def world_point(cls):
        (cx, cy) = Camera.singleton().rect.topleft
        (mx, my) = Mouse.screen_point()
        return (mx + cx, my + cy)

    @classmethod
    def move(cls, x, y):
        set_pos([x, y])

    @classmethod
    def center(cls):
        (screen_width, screen_height) = Screen.singleton().size
        position                      = (screen_width  // 2, screen_height // 2)
        Mouse.log(f"Moved to: {position}")
        set_pos(position)
