# Units:
#    Speed: frames per seconds

from .AnimationClock import AnimationClock
from .utils          import log_ex

class Rotation:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, orig_angle, step, fps):
        self.current     = orig_angle                  # Degrees
        self.target      = None                        # Degrees
        self.direction   = None                        # 1: left, -1: right
        self.step        = step                        # Rotation steps in degrees.

        raise NotImplementedError()
        self.frame_ratio = AnimationClock.singleton().fps / fps
        Rotation.log(f"frame_ratio={self.frame_ratio}")

    def show(self):
        Rotation.log(f"current={self.current} step={self.step}")
        if self.target is not None:
            msg = f"target={self.target} direction={self.direction}"
            if self.direction == 1:
                msg += "<left>"
            elif self.direction == -1:
                msg += "<right>"
            else:
                msg += "<invalid>"
            Rotation.log(msg)

    # Post-Conditions:
    # - is_done() is True
    def stop(self):
        Rotation.log("stop")
        self.target    = None
        self.direction = None
        assert self.is_done()

    def is_done(self):
        return self.target is None

    def rotate(self):
        self.current += self.direction * self.step
        if self.current >= 360:
            self.current = 0
        elif self.current < 0:
            self.current = 360 + self.current
        self.show()
        assert self.current % self.step == 0

    def update(self):
        raise NotImplementedError()
        if self.is_done():
            return
        if AnimationClock.singleton().frame_count % self.frame_ratio != 0:
            return
        self.rotate()
        if self.current == self.target:
            self.stop()

    def look(self, from_point, to_point):
        Rotation.log(f"look: from={from_point} to={to_point}")

        # Find the target angle.
        dx = from_point.x - to_point.x
        dy = from_point.y - to_point.y
        Rotation.log(f"look: dx={dx} dy={dy}")
        target = None
        if dx == 0:                              # top|bottom
            if dy == 0:
                Rotation.log("look: nothing to do: from_point == to_point")
                return
            elif dy > 0:                          # top
                target = 90
            else: # dy < 0                        # bottom
                target = 270
        elif dx > 0:                              # top-left|left|bottom-left
            if dy == 0:                           # left
                target = 180
            elif dy > 0:                          # top-left
                target = 135
            else: # dy < 0                        # bottom-left
                target = 225
        else: # dx < 0                            # top-right|right|bottom-right
            if dy == 0:                           # right
                target = 0
            elif dy > 0:                          # top-right
                target = 45
            else: # dy < 0                        # bottom-right
                target = 315
        assert target is not None
        if target == self.current:
            Rotation.log("look: nothing to do: target == current")
            return
        else:
            self.target = target

        # Find the rotation direction.
        if self.current < self.target:
            da = self.target - self.current
            if da < 180:
                self.direction = 1
            else:
                self.direction = -1
        else:
            da = self.current - self.target
            if da < 180:
                self.direction = -1
            else:
                self.direction = 1
        Rotation.log(f"look: da={da}")
        self.show()
