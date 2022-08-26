import pyxel

from .core  import Engine
from .utils import Config, logEx

class Animation:

    def log(msg):
        logEx(msg, category="Animation")

    def __init__(self, name, width, height, img, rate, isLoop, frames):
        self.name     = name
        self.width    = width
        self.height   = height
        self.img      = img
        self.frames   = frames
        self.ratio    = Engine.getFrameRate() / rate
        self.isLoop   = isLoop
        self.last     = len(frames) - 1
        self.current  = 0
        self.isPaused = True

    def reset(self):
        self.current = 0

    def pause(self):
        self.isPaused = True

    def resume(self):
        self.isPaused = False

    def isDone(self):
        return not self.isLoop and self.current == self.last

    def nextFrame(self):
        assert not self.isPaused
        assert not self.isDone()
        if self.current < self.last:
            self.current += 1
        elif self.current == self.last and self.isLoop:
            self.current = 0
        assert 0 <= self.current and self.current <= self.last

    def update(self):
        if self.isPaused or self.isDone():
            return
        if pyxel.frame_count % self.ratio != 0:
            return
        self.nextFrame()

    def drawAt(self, x, y):
        (fx, fy) = self.frames[self.current]
        pyxel.blt(x - self.width // 2, y - self.height // 2,
                  self.img, fx, fy, self.width, self.height, pyxel.COLOR_BLACK)

class AnimationManager:

    def log(msg):
        logEx(msg, category="AnimationManager")

    def __init__(self, img):
        self.animations = {}
        self.current    = None
        self.img        = img

    def add(self, name, frames, rate=10, width=8, height=8, isLoop=True):
        self.animations[name] = Animation(name, width, height, self.img, rate, isLoop, frames)

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
        if self.current.isPaused:
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

    def drawAt(self, x, y):
        if self.current is None:
            return
        self.current.drawAt(x, y)

        if Config.mustLog("Animation"):
            pyxel.text(x + 20, y + 1, f"A: {self.current.name}", 0)
