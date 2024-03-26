from os.path import join as path_join

from .AnimationManager import AnimationManager
from .Camera           import Camera
from .EngineClock      import EngineClock
from .utils            import Config, log_ex

# A sprite is something that is animated.
#
# A sprite's coordinates are expressed in pixels (via its `point` property, of
# type Point). There's no direct relationship between a sprite and a square.
class Sprite:

    def __init__(self, name, position):
        self.name        = f"{name}@{hex(id(self))}"
        self.position    = position
        self._animations = AnimationManager(name)

        self.offset = (0, 0)
        config      = Config.singleton().load( path_join(name, "sprite.json") )
        if "offset" in config:
            self.offset = config["offset"]

        self.log(f"Sprite '{name}':")
        self.log(f'    Position: {position}')

        EngineClock.singleton().register(self)
        EngineClock.singleton().resume(self)

    def log(self, msg):
        log_ex(msg, category="Sprite", name=self.name)

    # Shift position by the given offset.
    def shift(self, offset):
        (ox, oy)      = offset
        (x, y)        = self.position
        self.position = (x + ox, y + oy)

    def blit_debug_overlay(self):
        if not Config.singleton().must_log("Sprite"):
            return
        # FIXME
        # pyxel.text(p.x + 5, p.y, self.name, 0)
        raise NotImplementedError("Must replace pyxel.text")

    def blit(self):
        (px, py) = self.position
        (ox, oy) = self.offset
        self._animations.blit_current_at((px + ox, py + oy))

    def is_done(self):
        return False

    def add_time(self, _):
        self.blit()
