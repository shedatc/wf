from .AnimationManager import AnimationManager
from .utils            import Config, log_ex

# A sprite is something that is animated.
#
# A sprite's coordinates are expressed in pixels (via its `point` property, of
# type Point). There's no direct relationship between a sprite and a square.
class Sprite:

    def __init__(self, name, point):
        self.name        = f"{name}@{hex(id(self))}"
        self.point       = point
        self._animations = AnimationManager(name)

        Sprite.log(self, f'Name:     {name}')
        Sprite.log(self, f'Position: {point}')

    def log(self, msg):
        log_ex(msg, category="Sprite", name=self.name)

    def is_visible(self):
        if True:
            return True
        else:
            return self.position().is_visible()

    def update(self):
        pass

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

        (x, y) = self.point.screen()
        self._animations.blit_current_at(surface, x, y)
        # self.blit_debug_overlay(surface)
