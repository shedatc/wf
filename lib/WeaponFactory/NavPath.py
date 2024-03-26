from pygame      import Rect
from pygame.draw import rect as draw_rect

from .Compass import Compass
from .utils   import log_ex

# A navigation path is a list of hops. A hop is a square directly connected to
# the previous one.
class NavPath:

    def __init__(self, entity):
        self.entity = entity
        self.hop    = None
        self.hops   = []
        self.show()

    def log(self, msg):
        log_ex(msg, name=self.entity.name, category="NavPath")

    def clear(self):
        self.hop  = None
        self.hops = []

    def set(self, hops):
        assert len(hops) >= 1
        self.hop  = hops[0]
        self.hops = hops[1:]
        self.show()

    def next_hop(self):
        if len(self.hops) >= 1:
            self.hop  = self.hops[0]
            self.hops = self.hops[1:]

            c = Compass.singleton()
            if c.is_obstacle(self.hop):
                if len(self.hops) == 0:
                    self.log(f"Obstacle at destination {self.hop}")
                    self.log(f"Stop here")
                    self.hop  = None
                    self.hops = []
                else:
                    self.log(f"Obstacle at next hop {self.hop}")
                    self.log(f"Renavigate")
                    c.navigate(self.entity, self.destination())
        else:
            self.log(f"Done")
            self.hop  = None
            self.hops = []

    def destination(self):
        assert not self.is_done()
        if len(self.hops) >= 1:
            return self.hops[-1]
        elif self.hop is not None:
            return self.hop

    def is_done(self):
        return self.hop is None

    def show(self):
        hops = "[" + ", ".join([str(h) for h in self.hops]) + "]"
        self.log(f"hop={self.hop} hops={hops}")

    def blit_next_hop(self, surface, hop):
        if not hop.is_visible():
            return
        p = hop.point().screen()

        draw_rect(surface, (0, 0, 200),
                  Rect((p.x-2, p.y-2), (4, 4)))

    def blit_hop(self, surface, hop):
        if not hop.is_visible():
            return
        p = hop.point().screen()

        draw_rect(surface, (0, 0, 200),
                  Rect((p.x-1, p.y-1), (2, 2)))

    def blit_last_hop(self, surface, hop):
        if not hop.is_visible():
            return
        p = hop.point().screen()

        draw_rect(surface, (0, 0, 200),
                  Rect((p.x-2, p.y-2), (4, 4)))

    def blit(self, surface):
        if self.is_done():
            return
        if len(self.hops) >= 1:
            self.blit_next_hop(surface, self.hop)
            for hop in self.hops[0:-1]:
                self.blit_hop(surface, hop)
            hop = self.hops[-1]
            self.blit_last_hop(surface, hop)
        else:
            self.blit_last_hop(surface, self.hop)
