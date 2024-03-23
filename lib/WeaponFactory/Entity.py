from pygame      import Rect
from pygame.draw import rect as draw_rect

if False:
    from .navigation import Compass, NavPath
from .Physics    import Physics
from .Sprite     import Sprite
from .utils      import Config, Observable, log_ex

# An entity is a sprite that somehow obey the laws of physics.
#
# There's a relationship between the entity and squares via the navigation
# system (see `NavPath`).
class Entity(Sprite, Observable):

    def __init__(self, name, position, speed=0.0):
        Sprite.__init__(self, name, position)
        Observable.__init__(self)

        if False:
            self.nav_path     = NavPath(self)

        self._physics = Physics(self, speed=speed)

        self.moves       = []
        self.is_selected = False

    def log(self, msg):
        log_ex(msg, category="Entity", name=self.name)

    def select(self):
        self.is_selected = True

    def unselect(self):
        self.is_selected = False

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves.clear()

    def is_moving(self):
        raise NotImplementedError()
        return self.physics.target_position() is not None

    def look_at(self, hop):
        raise NotImplementedError()
        def look_at_hop():
            self.physics.look_at(hop.point())
        self.add_move(look_at_hop)

    def move_to(self, hop):
        raise NotImplementedError()
        def move_to_hop():
            p = hop.point()
            if Compass.singleton().is_obstacle(hop):
                Entity.log(self, f"move_to_hop: Cannot move, obstacle at target hop {hop}")
            else:
                self.physics.move_to(p)
                self.notify_observers("entity-moved",
                                      old_square=self.square(), new_square=hop)
        self.add_move(move_to_hop)

    def is_idle(self):
        raise NotImplementedError()
        return self.physics.is_done() and len(self.moves) == 0

    def stop(self):
        raise NotImplementedError()
        Entity.log(self, "stop")
        self.clear_moves()
        self.nav_path.clear()

    def navigate(self, hops):
        raise NotImplementedError()
        assert len(hops) >= 1
        Entity.log(self, "navigate")
        self.clear_moves()
        self.nav_path.set(hops)
        self.look_at(self.nav_path.hop)
        self.move_to(self.nav_path.hop)
        self.show()

    def next_hop(self):
        raise NotImplementedError()
        if self.nav_path.is_done():
            return

        self.nav_path.next_hop()
        if self.nav_path.is_done():
            Entity.log(self, f"next_hop: Destination {self.square()} reached")
        else:
            nh = self.nav_path.hop
            Entity.log(self, f"next_hop: Moving to hop {nh}")
            self.look_at(nh)
            self.move_to(nh)

    def next_move(self):
        raise NotImplementedError()
        if not self.physics.is_done():
            return

        if len(self.moves) >= 1:
            move = self.moves.pop(0)
            move()
        else:
            self.next_hop()

    def add_time(self, t):
        if self._physics is not None:
            self._physics.add_time(t)

    def blit_selection(self, surface):
        if not self.is_selected:
            return

        p  = self.position().screen()
        bw = 1
        w  = self.width  + bw + bw
        h  = self.height + bw + bw
        draw_rect(surface, (200, 0, 0),
                  Rect((p.x - w // 2, p.y - h // 2), (w, h)),
                  width=bw)

    def blit_nav_path(self, surface):
        raise NotImplementedError()
        if Config.singleton().must_log("NavPath"):
            self.nav_path.blit(surface)

    def blit_overlay(self, surface):
        raise NotImplementedError()
        if Config.singleton().must_log("Physics"):
            p = self.position().screen()
            self.physics.blit_at(surface, p.x, p.y)
