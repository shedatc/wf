from os.path     import join as path_join

from .Compass          import Compass
from .Config           import Config
from .NavPath          import NavPath
from .Observable       import Observable
from .Physics          import Physics
from .Sprite           import Sprite
from .utils            import log_ex

# An entity is a sprite that somehow obey the laws of physics.
#
# There's a relationship between the entity and squares via the navigation
# system (see `NavPath`).
class Entity(Sprite, Observable):

    def __init__(self, name, position):
        Sprite.__init__(self, name, position)
        Observable.__init__(self)

        orig_angle    = 0.0
        angular_speed = 0.0
        speed         = 0.0
        config = Config.singleton().load( path_join(name, "entity.json") )
        if "orig_angle" in config:
            orig_angle = config["orig_angle"]
        if "angular_speed" in config:
            angular_speed = config["angular_speed"]
        if "speed" in config:
            speed = config["speed"]

        self.log(f"Speed: {speed} px/ms")

        if False:
            self.nav_path     = NavPath(self)


        self.moves       = []
        self._physics    = Physics(self,
                                   speed=speed,
                                   orig_angle=orig_angle, angular_speed=angular_speed)
        self.is_selected = False

    def log(self, msg):
        log_ex(msg, category="Entity", name=self.name)

    def select(self):
        self.is_selected = True
        self.set_animation_state("entity", True)

    def unselect(self):
        self.is_selected = False
        self.set_animation_state("entity", False)

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves.clear()

    def is_moving(self):
        return self._physics.is_translating()

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

    def blit(self):
        self.blit_debug()
        Sprite.blit(self)

    def blit_nav_path(self, surface):
        raise NotImplementedError()
        if Config.singleton().must_log("NavPath"):
            self.nav_path.blit(surface)

    def blit_debug(self):
        self._physics.blit_debug()
