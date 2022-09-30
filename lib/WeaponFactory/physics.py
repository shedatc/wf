# Units:
#    Speed: frames per seconds

from .arena import Point
from .core  import Engine
from .math  import Vector
from .utils import Config, log_ex

class Physics:

    def log(msg):
        log_ex(msg, category="Physics")

    def __init__(self, orig_angle, rotation_speed, orig_point, translation_speed):
        self.rotation    = Rotation(orig_angle, 22.5, rotation_speed)
        self.translation = Translation(orig_point, translation_speed)

    def show(self):
        Physics.log(f"position={self.position()} orientation={self.orientation()}")
        Physics.log(f"rotating={not self.rotation.is_done()}")
        Physics.log(f"translating={not self.translation.is_done()}")

    def orientation(self):
        return self.rotation.current

    def position(self):
        return self.translation.current

    def target_position(self):
        return self.translation.target

    def look_at(self, point):
        self.rotation.look(self.position(), point)

    def move_to(self, point):
        self.translation.move_to(point)

    def is_done(self):
        return self.rotation.is_done() and self.translation.is_done()

    def update(self):
        self.rotation.update()
        self.translation.update()

    def blit_at(self, surface, x, y):
        if False:
            x += 20
            y += 8
            # FIXME
            # pyxel.text(x, y, f"P: {self.position()}", 0)
            raise NotImplementedError("Must replace pyxel.text")
            y += 8
            # pyxel.text(x, y, f"O: {self.orientation()}°", 0)
            y += 8
            # pyxel.text(x, y, f"V: {self.translation.vector}", 0)

class Rotation:

    def log(msg):
        log_ex(msg, category="Rotation")

    def __init__(self, orig_angle, step, fps):
        self.current     = orig_angle                  # Degrees
        self.target      = None                        # Degrees
        self.direction   = None                        # 1: left, -1: right
        self.step        = step                        # Rotation steps in degrees.
        self.frame_ratio = Engine.singleton().fps / fps
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
        if self.is_done():
            return
        if Engine.singleton().frame_count % self.frame_ratio != 0:
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

class Translation:

    def log(msg):
        log_ex(msg, category="Translation")

    def __init__(self, current, fps):
        self.current     = current
        self.target      = None
        self.distance    = None
        self.vector      = None
        self.vector_len  = None
        self.frame_ratio = Engine.singleton().fps / fps
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
        if self.is_done():
            return
        if Engine.singleton().frame_count % self.frame_ratio != 0:
            return
        self.translate()
        if self.distance is None or self.distance <= 0:
            self.stop()
        self.show()
