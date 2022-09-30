from pygame import Rect

from .core  import Engine
from .utils import Config, log_ex

class Animation:

    def log(msg):
        log_ex(msg, category="Animation")

    def __init__(self, name, width, height, surface, rate, is_loop, frames):
        self.name      = name
        self.width     = width
        self.height    = height
        self.surface   = surface
        self.frames    = frames
        self.ratio     = Engine.singleton().fps / rate
        self.is_loop   = is_loop
        self.last      = len(frames) - 1
        self.current   = 0
        self.is_paused = True

    def reset(self):
        self.current = 0

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def is_done(self):
        return not self.is_loop and self.current == self.last

    def next_frame(self):
        assert not self.is_paused
        assert not self.is_done()
        if self.current < self.last:
            self.current += 1
        elif self.current == self.last and self.is_loop:
            self.current = 0
        assert 0 <= self.current and self.current <= self.last

    def update(self):
        if self.is_paused or self.is_done():
            return
        if Engine.singleton().frame_count % self.ratio != 0:
            return
        self.next_frame()

    def blit_at(self, surface, x, y):
        (fx, fy) = self.frames[self.current]
        surface.blit(self.surface,                                   # source
                     (x - self.width // 2, y - self.height // 2),    # dest
                     area=Rect((fx, fy), (self.width, self.height)))
        # FIXME
        # pyxel.blt(x - self.width // 2, y - self.height // 2,
        #           self.img, fx, fy, self.width, self.height, pyxel.COLOR_BLACK)
        # raise NotImplementedError("Must replace pyxel.blt")

class AnimationManager:

    def log(msg):
        log_ex(msg, category="AnimationManager")

    def __init__(self, surface):
        self.animations = {}
        self.current    = None
        self.surface    = surface

    def add(self, name, frames, rate=10, width=8, height=8, is_loop=True):
        self.animations[name] = Animation(name, width, height, self.surface, rate, is_loop, frames)

    def reset(self):
        self.current = None

    def select(self, name):
        AnimationManager.log(f"select: {name}")
        self.current = self.animations[name]

    def pause(self):
        AnimationManager.log(f"pause: {self.current.name}")
        self.current.pause()

    def resume(self):
        AnimationManager.log(f"resume: {self.current.name}")
        self.current.resume()

    def toggle(self):
        AnimationManager.log(f"toggle")
        if self.current.is_paused:
            self.current.resume()
        else:
            self.current.pause()

    def frame(self):
        return self.current.current

    def name(self):
        f = self.current
        return f"{f.name}[{f.current}]"

    def update(self):
        self.current.update()

    def blit_at(self, surface, x, y):
        if self.current is None:
            return
        self.current.blit_at(surface, x, y)

        if False:
            if Config.singleton().must_log("Animation"):
                # FIXME
                # pyxel.text(x + 20, y + 1, f"A: {self.current.name}", 0)
                raise NotImplementedError("Must replace pyxel.text")
