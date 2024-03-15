import pygame

from pygame import Rect

from .Arena  import Arena
from .Square import Square
from .utils  import log_ex

class Region:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = Region()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        self.start      = None
        self.end        = None
        self.is_enabled = False
        Region.log(f"start={self.start} end={self.end} is_enabled={self.is_enabled}")

    def enable(self):
        if self.is_enabled:
            Region.log("already enabled")
        else:
            self.start      = Square(0, 0).from_mouse()
            self.end        = Square(0, 0).from_mouse()
            self.is_enabled = True
            Region.log("enabled")

    # Return the entities belonging to the region. Return None if already
    # disabled.
    def disable(self):
        if self.is_enabled:
            Region.log("disabled")
            entities        = self.get_entities()
            self.start      = None
            self.end        = None
            self.is_enabled = False
            return entities
        else:
            Region.log("already disabled")
            return None

    def is_empty(self):
        self.end is None or self.start == self.end

    def update(self):
        if not self.is_enabled:
            return
        if self.end is not None:
            self.end.from_mouse()
            Region.log(f"start={self.start} end={self.end} is_enabled={self.is_enabled}")

    def get_origin(self):
        assert self.is_enabled
        s = self.start
        e = self.end
        u = min(s.u, e.u)
        v = min(s.v, e.v)
        return Square(u, v)

    def get_width(self):
        assert self.is_enabled
        return abs(self.start.u - self.end.u) + 1

    def get_height(self):
        assert self.is_enabled
        return abs(self.start.v - self.end.v) + 1

    def blit(self, surface):
        if not self.is_enabled:
            return

        # Draw the square-level region
        o  = self.get_origin().point().screen()
        Region.log(f"origin={o}")

        (square_width, square_height) = Arena.singleton().square_size
        pixels = Rect((o.x - square_width // 2,         o.y - square_height // 2),
                      (self.get_width() * square_width, self.get_height() * square_height))
        pygame.draw.rect(surface, (200, 0, 0), pixels, width=1)

    # Return the entities that are part of the region.
    def get_entities(self):
        entities = []
        o        = self.get_origin()
        a        = Arena.singleton()
        for v in range(o.v, o.v + self.get_height()):
            for u in range(o.u, o.u + self.get_width()):
                e = a.entities_at_square(u, v)
                Region.log(f"e={e} len(e)={len(e)}")
                if len(e) >= 1:
                    # If at least one entity is on the square, add only the
                    # first one to handle stacking.
                    entities.append(e[0])
        Region.log(f"entities={entities}")
        return entities
