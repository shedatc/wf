from pygame      import Rect
from pygame.draw import rect as draw_rect

from .AnimationPlayer import AnimationPlayer
from .Arena           import Arena
from .Compass         import Compass
from .Config          import Config
from .EngineClock     import EngineClock
from .Screen          import Screen
from .colors          import COLOR_BLUE
from .utils           import log_ex

# A navigation path is a list of hops. A hop is a point in world coordinates.
class NavPath:

    def __init__(self, entity):
        self.entity = entity
        self.hop    = None
        self.hops   = []

        self._next_hop = AnimationPlayer("nav-point", select ="Next Hop")
        self._hop      = AnimationPlayer("nav-point", select ="Hop")
        self._last_hop = AnimationPlayer("nav-point", select ="Last Hop")

    def log(self, msg):
        log_ex(msg, name=self.entity.name, category="NavPath")

    def clear(self):
        self.hop  = None
        self.hops = []

    def set(self, hops):
        assert len(hops) >= 1
        self.hop  = hops[0]
        self.hops = hops[1:]
        self.log(f"Navigation path:")
        self.log(f"    {self.hop} ★")
        for h in self.hops:
            self.log(f"    {h}")

    def next_hop(self):
        if len(self.hops) == 0:
            self.log(f"Done")
            self.hop  = None
            return

        self.hop   = self.hops[0]
        self.hops  = self.hops[1:]
        c          = Compass.singleton()
        a          = Arena.singleton()
        hop_square = a.square(self.hop)
        if not c.is_obstacle(hop_square):
            return
        if len(self.hops) == 0:
            self.log(f"Obstacle at destination {hop_square} ({self.hop}); stop here")
            self.hop = None
            return
        self.log(f"Obstacle at next hop {hop_square} ({self.hop}); renavigate")
        c.find_path(self.entity_square(), self.destination_square())

    def entity_square(self):
        return Arena.singleton().square(self.entity.position)

    def destination_square(self):
        assert not self.is_done()
        if len(self.hops) >= 1:
            hop = self.hops[-1]
        elif self.hop is not None:
            hop = self.hop
        return Arena.singleton().square(hop)

    def is_done(self):
        return self.hop is None

    def _build_animations(self):
        animations = []
        if len(self.hops) >= 1:
            animations.append((self.hops[-1], self._next_hop.show().resume()))
            for hop in self.hops[0:-1]:
                animations.append((hop, self._hop.show().resume()))
            hop = self.hops[-1]
            animations.append((hop, self._last_hop.show().resume()))
        else:
            animations.append((self.hop, self._last_hop.show().resume()))
        return animations

    def blit_debug(self):
        if not Config.singleton().must_log("NavPath"):
            return
        if self.is_done():
            return
        for (hop, ap) in self._build_animations():
            ap.blit_at(hop)
