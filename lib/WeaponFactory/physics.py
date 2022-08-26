# Units:
#    Speed: frames per seconds

import pyxel

from .arena import Point
from .core  import Engine
from .math  import Vector
from .utils import Config, logEx

class Physics:

    def log(msg):
        logEx(msg, category="Physics")

    def __init__(self, origAngle, rotationSpeed, origPoint, translationSpeed):
        self.rotation    = Rotation(origAngle, 22.5, rotationSpeed)
        self.translation = Translation(origPoint, translationSpeed)

    def show(self):
        Physics.log(f"position={self.position()} orientation={self.orientation()}")
        Physics.log(f"inRotation={not self.rotation.isDone()}")
        Physics.log(f"inTranslaton={not self.translation.isDone()}")

    def orientation(self):
        return self.rotation.current

    def position(self):
        return self.translation.current

    def targetPosition(self):
        return self.translation.target

    def lookAt(self, point):
        self.rotation.look(self.position(), point)

    def moveTo(self, point):
        self.translation.moveTo(point)

    def isDone(self):
        return self.rotation.isDone() and self.translation.isDone()

    def update(self):
        self.rotation.update()
        self.translation.update()

    def drawAt(self, x, y):
        if False:
            x += 20
            y += 8
            pyxel.text(x, y, f"P: {self.position()}", 0)
            y += 8
            pyxel.text(x, y, f"O: {self.orientation()}°", 0)
            y += 8
            pyxel.text(x, y, f"V: {self.translation.vector}", 0)

class Rotation:

    def log(msg):
        logEx(msg, category="Rotation")

    def __init__(self, origAngle, step, fps):
        self.current    = origAngle                   # Degrees
        self.target     = None                        # Degrees
        self.direction  = None                        # 1: left, -1: right
        self.step       = step                        # Rotation steps in degrees.
        self.frameRatio = Engine.getFrameRate() / fps
        Rotation.log(f"frameRatio={self.frameRatio}")

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
    # - isDone() is True
    def stop(self):
        Rotation.log("stop")
        self.target    = None
        self.direction = None
        assert self.isDone()

    def isDone(self):
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
        if self.isDone():
            return
        if pyxel.frame_count % self.frameRatio != 0:
            return
        self.rotate()
        if self.current == self.target:
            self.stop()

    def look(self, fromPoint, toPoint):
        Rotation.log(f"look: from={fromPoint} to={toPoint}")

        # Find the target angle.
        dx = fromPoint.x - toPoint.x
        dy = fromPoint.y - toPoint.y
        Rotation.log(f"look: dx={dx} dy={dy}")
        target = None
        if dx == 0:                              # top|bottom
            if dy == 0:
                Rotation.log("look: nothing to do: fromPoint == toPoint")
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
        logEx(msg, category="Translation")

    def __init__(self, current, fps):
        self.current    = current
        self.target     = None
        self.distance   = None
        self.vector     = None
        self.vectorLen  = None
        self.frameRatio = Engine.getFrameRate() / fps
        Translation.log(f"frameRatio={self.frameRatio}")

    def show(self):
        Translation.log(f"current={self.current}")
        if self.target is not None:
            Translation.log(f"target={self.target} distance={self.distance}")
            Translation.log(f"vector={self.vector} vectorLen={self.vectorLen}")

    # Post-Conditions:
    # - isDone() is True
    def stop(self):
        Translation.log("stop")
        self.current   = self.target
        self.target    = None
        self.distance  = None
        self.vector    = None
        self.vectorLen = None
        assert self.isDone()

    def isDone(self):
        return self.target is None

    def translate(self):
        Translation.log("translate")
        assert self.current is not None
        assert self.vector is not None
        self.current.x += self.vector.x
        self.current.y += self.vector.y
        self.distance  -= self.vectorLen

    def moveTo(self, point):
        assert isinstance(point, Point)
        Translation.log("moveTo")
        self.target = point
        v           = Vector(self.target.x - self.current.x,
                             self.target.y - self.current.y)
        Translation.log(f"moveTo: v={v}")
        self.distance = v.getLength()
        if self.distance >= 1:
            self.vector    = v.getUnit().scale(self.distance // self.frameRatio)
            self.vectorLen = self.vector.getLength()
            assert self.vectorLen <= self.distance
        else:
            self.stop()
        self.show()

    def update(self):
        if self.isDone():
            return
        if pyxel.frame_count % self.frameRatio != 0:
            return
        self.translate()
        if self.distance is None or self.distance <= 0:
            self.stop()
        self.show()
