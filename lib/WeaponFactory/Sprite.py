from os.path import join as path_join

from .AnimationPlayer import AnimationPlayer
from .Config          import Config
from .EngineClock     import EngineClock
from .utils           import log_ex

# A sprite is something that is animated.
#
# A sprite's coordinates are expressed in pixels (via its `point` property, of
# type Point). There's no direct relationship between a sprite and a square.
class Sprite:

    def __init__(self, name, position):
        self.name     = f"{name}@{hex(id(self))}"
        self.position = position

        config = Config.singleton().load( path_join(name, "sprite.json") )

        self._animations      = {}
        self._animation_order = []
        for animation_config in config["animations"]:
            offset           = animation_config["offset"]
            name             = animation_config["name"]
            select           = animation_config["select"]
            enable           = animation_config["enable"]
            animation_player = AnimationPlayer(name, select=select)
            if enable:
                animation_player.resume()
                animation_player.show()
                e = "enabled"
            else:
                e = "disabled"
            o = len(self._animation_order)
            self._animations[name] = {
                "offset":           offset,
                "animation_player": animation_player,
                "enable":           enable
            }
            self._animation_order.append(name)

        # Log some data
        self.log(f"Sprite '{name}':")
        self.log(f'    Position: {position}')
        self.log(f'    Animations:')
        o = 0
        for name, a in self._animations.items():
            enable = a["enable"]
            offset = a["offset"]
            select = a["animation_player"].current.name
            if enable:
                e = "enabled"
            else:
                e = "disabled"
            self.log(f"        #{o} {name} at {offset} '{select}' {e}")
            o += 1

        EngineClock.singleton().register(self).resume(self)

    def __del__(self):
        EngineClock.singleton().unregister(self)

    def log(self, msg):
        log_ex(msg, category="Sprite", name=self.name)

    # Shift position by the given offset.
    def shift(self, offset):
        (ox, oy)      = offset
        (x, y)        = self.position
        self.position = (x + ox, y + oy)

    def set_animation_state(self, name, enable):
        self._animations[name]["enable"] = enable
        player = self._animations[name]["animation_player"]
        if enable:
            player.resume()
            player.show()
        else:
            player.pause()
            player.hide()

    def blit_debug_overlay(self):
        if not Config.singleton().must_log("Sprite"):
            return
        # FIXME
        # pyxel.text(p.x + 5, p.y, self.name, 0)
        raise NotImplementedError("Must replace pyxel.text")

    def blit(self):
        (px, py) = self.position
        for name in self._animation_order:
            a = self._animations[name]
            if not a["enable"]:
                continue
            (ox, oy) = a["offset"]
            a["animation_player"].blit_at((px + ox, py + oy))

    def is_done(self):
        return False

    def add_time(self, _):
        self.blit()
