from pygame      import Rect
from pygame.draw import rect as draw_rect

from .Arena  import Arena
from .Camera import Camera
from .Mouse  import Mouse
from .Screen import Screen
from .const  import COLOR_RED, COLOR_WHITE, DEBUG_REGION
from .utils  import log_ex

class Region:

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
        self._anchor     = (0, 0)
        self._cursor     = (0, 0)
        self._is_enabled = False
        self._rect       = Rect((0, 0), (0, 0))

        Region._singleton = self

    def __repr__(self):
        return "<Region " + " ".join([
            f"rect={self._rect}",
            # f"anchor={self._anchor}",
            # f"cursor={self._cursor}",
            # f"is_enabled={self._is_enabled}",
        ]) + ">"

    def square_at_mouse(self):
        return Arena.singleton().square( Mouse.world_point() )

    def enable(self):
        if self._is_enabled:
            Region.log(f"Already enabled: anchor={self._anchor} cursor={self._cursor}" \
                       + f" rect={self._rect}")
            return

        mouse_point      = Mouse.screen_point()
        self._anchor     = mouse_point
        self._cursor     = mouse_point
        self._rect       = Rect(self._anchor, (0, 0))
        self._is_enabled = True
        Region.log(f"Enabled: anchor={self._anchor} cursor={self._cursor} rect={self._rect}")

    def update_cursor(self):
        if not self._is_enabled:
            return

        self._cursor = Mouse.screen_point()

        # Update the rectangle.
        (ax, ay)   = self._anchor
        (cx, cy)   = self._cursor
        (tlx, tly) = ( min(ax, cx),   min(ay, cy) ) # top left corner
        (brx, bry) = ( max(ax, cx),   max(ay, cy) ) # bottom right corner
        (w, h)     = ( brx - tlx + 1, bry - tly + 1 )
        self._rect = Rect((tlx, tly), (w, h))

        assert self._rect.collidepoint(self._anchor), "Anchor must be part of the rectangle"
        assert self._rect.collidepoint(self._cursor), "Cursor must be part of the rectangle"

    def disable(self):
        if not self._is_enabled:
            Region.log("Already disabled")
            return None
        rect             = self._rect.copy()
        self._rect       = Rect((0, 0), (0, 0))
        self._is_enabled = False
        Region.log(f"Disabled: rect={rect}")
        return None

    def blit(self):
        if not self._is_enabled:
            return

        # Display the region.
        if DEBUG_REGION:
            Screen.singleton().draw_rect(COLOR_RED, self._rect, 1)

        # Display the squares that are part of the region.
        r      = self._rect.inflate(-1, -1)
        a      = Arena.singleton()
        tls    = a.square_rect(r.topleft)
        brs    = a.square_rect(r.bottomright)
        (w, h) = (brs.x - tls.x + brs.w, brs.y - tls.y + brs.h)
        Screen.singleton().draw_rect(COLOR_WHITE,
                                     Rect(tls.topleft, (w, h)),
                                     1)

    # Return the entities that are part of the region.
    def get_entities(self):
        raise NotImplementedError()
        entities = []
        o        = self.origin()
        a        = Arena.singleton()
        for v in range(o.v, o.v + self.rect.height):
            for u in range(o.u, o.u + self.rect.width):
                e = a.entities_at_square(u, v)
                Region.log(f"e={e} len(e)={len(e)}")
                if len(e) >= 1:
                    # If at least one entity is on the square, add only the
                    # first one to handle stacking.
                    entities.append(e[0])
        Region.log(f"entities={entities}")
        return entities
