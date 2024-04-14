from pygame      import Rect
from pygame.draw import rect as draw_rect

from .Compass import Compass
from .Config  import Config
from .Screen  import Screen
from .colors  import COLOR_BLUE
from .utils   import log_ex

# A navigation path is a list of hops. A hop is a point in world coordinates.
class NavPath:

    def __init__(self, entity):
        self.entity = entity
        self.hop    = None
        self.hops   = []

    def log(self, msg):
        log_ex(msg, name=self.entity.name, category="NavPath")

    def clear(self):
        self.hop  = None
        self.hops = []

    def set(self, hops):
        assert len(hops) >= 1
        self.hop  = hops[0]
        self.hops = hops[1:]

    def next_hop(self):
        if len(self.hops) == 0:
            self.log(f"Done")
            self.hop  = None
            return

        self.hop  = self.hops[0]
        self.hops = self.hops[1:]

        c = Compass.singleton()
        if not c.is_obstacle(self.hop):
            return
        if len(self.hops) == 0:
            self.log(f"Obstacle at destination {self.hop}; stop here")
            self.hop = None
            return
        self.log(f"Obstacle at next hop {self.hop}; renavigate")
        c.find_path(self.entity, self.destination())

    def destination(self):
        assert not self.is_done()
        if len(self.hops) >= 1:
            return self.hops[-1]
        elif self.hop is not None:
            return self.hop

    def is_done(self):
        return self.hop is None

    def _blit_next_hop(self, hop):
        Screen.singleton().draw_point(hop, color=COLOR_BLUE, width=4)

    def _blit_hop(self, hop):
        Screen.singleton().draw_point(hop, color=COLOR_BLUE, width=2)

    def _blit_last_hop(self, hop):
        Screen.singleton().draw_point(hop, color=COLOR_BLUE, width=4)

    def blit_debug(self):
        if not Config.singleton().must_log("NavPath"):
            return
        if self.is_done():
            return
        if len(self.hops) >= 1:
            self._blit_next_hop(self.hop)
            for hop in self.hops[0:-1]:
                self._blit_hop(hop)
            hop = self.hops[-1]
            self._blit_last_hop(hop)
        else:
            self._blit_last_hop(self.hop)
