# Units:
#    Speed: frames per seconds

from .arena          import Point
from .math           import Vector
from .AnimationClock import AnimationClock
from .utils          import log_ex

class Translation:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, current, fps):
        self.current     = current
        self.target      = None
        self.distance    = None
        self.vector      = None
        self.vector_len  = None

        raise NotImplementedError()
        self.frame_ratio = AnimationClock.singleton().fps / fps
        Translation.log(f"frame_ratio={self.frame_ratio}")

    def show(self):
        Translation.log(f"current={self.current}")
        if self.target is not None:
            Translation.log(f"target={self.target} distance={self.distance}")
            Translation.log(f"vector={self.vector} vector_len={self.vector_len}")

    # Post-Conditions:
    # - is_done() is True
    def stop(self):
        Translation.log("stop")
        self.current    = self.target
        self.target     = None
        self.distance   = None
        self.vector     = None
        self.vector_len = None
        assert self.is_done()

    def is_done(self):
        return self.target is None

    def translate(self):
        Translation.log("translate")
        assert self.current is not None
        assert self.vector is not None
        self.current.x += self.vector.x
        self.current.y += self.vector.y
        self.distance  -= self.vector_len

    def move_to(self, point):
        raise NotImplementedError()
        assert isinstance(point, Point)
        Translation.log("move_to")
        self.target = point
        v           = Vector(self.target.x - self.current.x,
                             self.target.y - self.current.y)
        Translation.log(f"move_to: v={v}")
        self.distance = v.get_length()
        if self.distance >= 1:
            self.vector    = v.get_unit().scale(self.distance // self.frame_ratio)
            self.vector_len = self.vector.get_length()
            assert self.vector_len <= self.distance
        else:
            self.stop()
        self.show()

    def update(self):
        raise NotImplementedError()
        if self.is_done():
            return
        if AnimationClock.singleton().frame_count % self.frame_ratio != 0:
            return
        self.translate()
        if self.distance is None or self.distance <= 0:
            self.stop()
        self.show()
