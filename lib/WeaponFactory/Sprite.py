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

    def blit_at(self, position):
        self._animations.blit_current_at(position)

    def is_done(self):
        return False

    def add_time(self, t):
        c               = Camera.singleton()
        (cx, cy)        = c.rect.topleft
        (x, y)          = self.position
        screen_position = (x - cx, y - cy)
        if False:
            self.blit_at(self.position)
        else:
            self.blit_at(screen_position)
