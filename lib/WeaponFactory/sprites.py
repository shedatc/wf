import pygame

from pygame import Rect

from .animation  import Animation, AnimationManager
from .arena      import Arena
from .navigation import Compass, NavPath
from .physics    import Physics
from .resources  import Resources
from .utils      import Config, Observable, log_ex

# A sprite is something that is animated.
#
# A sprite's coordinates are expressed in pixels (via its `point` property, of
# type Point). There's no direct relationship between a sprite and a square.
class Sprite:

    def __init__(self, name, orig_point, width, height):
        self.name      = f"{name}@{hex(id(self))}"
        self.point     = orig_point
        self.width     = width
        self.height    = height
        self.animation = AnimationManager(name)

        Sprite.log(self, f'point={orig_point} size={width}x{height}')

    def log(self, msg):
        log_ex(msg, category="Sprite", name=self.name)

    def position(self):
        return self.point

    def update(self):
        self.update_animation()

    def update_animation(self):
        self.animation.update()

    def is_visible(self):
        return self.position().is_visible()

    def blit_debug_overlay(self, surface):
        if not Config.singleton().must_log("Sprite"):
            return
        if False:
            # FIXME
            # pyxel.text(p.x + 5, p.y, self.name, 0)
            raise NotImplementedError("Must replace pyxel.text")

    def blit(self, surface):
        if not self.is_visible():
            return

        p = self.position().screen()
        self.animation.blit_at(surface, p.x, p.y)
        # self.blit_debug_overlay(surface)

# An entity is a sprite that somehow obey the laws of physics.
#
# There's a relationship between the entity and squares via the navigation
# system (see `NavPath`).
class Entity(Sprite, Observable):

    def __init__(self, name, orig_point, width, height, rot_step, rot_fps, tr_fps):
        Sprite.__init__(self, name, orig_point, width, height)
        Observable.__init__(self)

        self.nav_path     = NavPath(self)
        self.physics     = Physics(0, rot_fps, orig_point, tr_fps)
        self.moves       = []
        self.is_selected = False

    def log(self, msg):
        log_ex(msg, category="Entity", name=self.name)

    def select(self):
        self.is_selected = True

    def unselect(self):
        self.is_selected = False

    def show(self):
        Entity.log(self, f"moves={len(self.moves)} nav_path={self.nav_path.is_done()}")
        Entity.log(self, f"square={self.square()} target_square={self.target_square()}")
        Entity.log(self, f"is_moving={self.is_moving()} is_idle={self.is_idle()}")
        self.physics.show()

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves.clear()

    def position(self):
        return self.physics.position()

    def target_position(self):
        return self.physics.target_position()

    def square(self):
        return self.physics.position().square()

    def target_square(self):
        p = self.physics.target_position()
        if p is None:
            return None
        else:
            return p.square()

    def is_moving(self):
        return self.physics.target_position() is not None

    def look_at(self, hop):
        def look_at_hop():
            self.physics.look_at(hop.point())
        self.add_move(look_at_hop)

    def move_to(self, hop):
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
        return self.physics.is_done() and len(self.moves) == 0

    def stop(self):
        Entity.log(self, "stop")
        self.clear_moves()
        self.nav_path.clear()

    def navigate(self, hops):
        assert len(hops) >= 1
        Entity.log(self, "navigate")
        self.clear_moves()
        self.nav_path.set(hops)
        self.look_at(self.nav_path.hop)
        self.move_to(self.nav_path.hop)
        self.show()

    def next_hop(self):
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
        if not self.physics.is_done():
            return

        if len(self.moves) >= 1:
            move = self.moves.pop(0)
            move()
        else:
            self.next_hop()

    def update(self):
        self.physics.update()
        self.next_move()
        Sprite.update(self)

    def blit_selection(self, surface):
        if not self.is_selected:
            return

        p  = self.position().screen()
        bw = 1
        w  = self.width  + bw + bw
        h  = self.height + bw + bw
        pygame.draw.rect(surface, (200, 0, 0),
                         Rect((p.x - w // 2, p.y - h // 2), (w, h)),
                         width=bw)

    def blit_nav_path(self, surface):
        if Config.singleton().must_log("NavPath"):
            self.nav_path.blit(surface)

    def blit_overlay(self, surface):
        if Config.singleton().must_log("Physics"):
            p = self.position().screen()
            self.physics.blit_at(surface, p.x, p.y)

    def blit(self, surface):
        Sprite.blit(self, surface)
