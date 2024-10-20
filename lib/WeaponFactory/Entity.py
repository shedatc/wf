from os.path import join as path_join

from .Arena      import Arena
from .Compass    import Compass
from .Config     import Config
from .NavPath    import NavPath
from .Observable import Observable
from .Physics    import Physics
from .Sprite     import Sprite
from .utils      import log_ex

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

        self._nav_path   = NavPath(self)
        self._physics    = Physics(self,
                                   speed=speed,
                                   orig_angle=orig_angle, angular_speed=angular_speed)
        self._moves      = []
        self.is_selected = False

    def __str__(self):
        return f"<Entity {self.name}>"

    def target_position(self):
        return self._physics.target_position()

    def log(self, msg):
        log_ex(msg, category="Entity", name=self.name)

    def select(self):
        self.is_selected = True
        self.set_animation_state("entity", True)

    def unselect(self):
        self.is_selected = False
        self.set_animation_state("entity", False)

    def is_moving(self):
        return self._physics.is_translating()

    # Queue a rotation aiming to look at the given world point (hop) .
    def _look_at(self, world_point):
        def look_at_hop():
            self._physics.look_at(world_point)
        self._moves.append(look_at_hop)

    # Queue a straight line move to the given world point (hop) .
    def _jump_to(self, world_point):
        world_square = Arena.singleton().square(world_point)
        def jump_to_hop():
            Entity.log(self, f"_jump_to_hop: {world_point} → {world_square}")
            if Compass.singleton().is_obstacle(world_square):
                Entity.log(self, f"_jump_to_hop: Cannot jump, obstacle at target square {world_square}")
                return
            self._physics.move_to(world_point)
            self.notify_observers("entity-moved",
                                  old_position=self.position, new_position=world_point)
        self._moves.append(jump_to_hop)

    def is_idle(self):
        return self._physics.is_done() and self._moves == []

    def stop(self):
        Entity.log(self, "stop")
        self._moves.clear()
        self._nav_path.clear()

    # hops must be a list of positions in world coordinates.
    def navigate(self, hops):
        assert len(hops) >= 1
        Entity.log(self, "navigate")
        self._moves.clear()
        self._nav_path.set(hops)
        self._look_at(self._nav_path.hop)
        self._jump_to(self._nav_path.hop)

    def next_hop(self):
        if self._nav_path.is_done():
            return

        self._nav_path.next_hop()
        if self._nav_path.is_done():
            Entity.log(self, f"next_hop: Destination {self.position} reached")
        else:
            nh = self._nav_path.hop
            Entity.log(self, f"next_hop: Moving to hop {nh}")
            self._look_at(nh)
            self._jump_to(nh)

    def next_move(self):
        if not self._physics.is_done():
            return

        if len(self._moves) >= 1:
            move = self._moves.pop(0)
            move()
        else:
            self.next_hop()

    def blit(self):
        Sprite.blit(self)
        self.blit_debug()

    def blit_debug(self):
        if not Config.singleton().must_log("Entity"):
            return
        self._physics.blit_debug()
        self._nav_path.blit_debug()

    def is_done(self):
        return Sprite.is_done(self) and self._physics.is_done() and self._moves == []

    def add_time(self, t):
        Sprite.add_time(self, t)
        self.next_move()
