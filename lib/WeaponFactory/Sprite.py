from .AnimationManager import AnimationManager
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

        Sprite.log(self, f'Name:     {name}')
        Sprite.log(self, f'Position: {position}')

    def log(self, msg):
        log_ex(msg, category="Sprite", name=self.name)

    def update(self):
        pass

    def blit_debug_overlay(self):
        if not Config.singleton().must_log("Sprite"):
            return
        # FIXME
        # pyxel.text(p.x + 5, p.y, self.name, 0)
        raise NotImplementedError("Must replace pyxel.text")

    def blit_at(self, position):
        self._animations.blit_current_at(position)
