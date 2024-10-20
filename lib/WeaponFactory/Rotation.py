from math        import asin, degrees, fabs, pi
from pygame      import Rect
from pygame.math import Vector2

from .Config      import Config
from .EngineClock import EngineClock
from .Screen      import Screen
from .colors      import COLOR_BLUE, COLOR_GREEN, COLOR_RED
from .utils       import log_ex

class Rotation:

    CW  = -1 # Clockwize
    CCW =  1 # Counterclockwize

    def log(self, msg):
        log_ex(msg, name=self.entity.name, category="Rotation")

    def __init__(self, entity, orig_angle, angular_speed):
        self.angular_speed = angular_speed # °/ms
        self.current_angle = orig_angle    # °
        self.direction     = Rotation.CCW  # CW or CCW
        self.entity        = entity
        self.target_angle  = orig_angle    # °
        EngineClock.singleton().register(self)

    def __del__(self):
        EngineClock.singleton().unregister(self)

    def _angle_from_vector(self, v):
        assert type(v) is Vector2
        u        = v / v.length()
        (_, uy)  = u.xy
        angle    = asin(fabs(uy))
        (vx, vy) = v.xy
        if vx >= 0.0:
            if vy >= 0.0:
                angle = 2*pi - angle
            else: # vy < 0
                pass
        else: # vx < 0.0
            if vy >= 0.0:
                angle = pi + angle
            else: # vy < 0.0
                angle = pi - angle
        return degrees(angle)

    def look_at(self, target):
        (ex, ey)          = self.entity.position
        (tx, ty)          = target
        et                = Vector2(tx - ex, ty - ey)
        self.target_angle = self._angle_from_vector(et)

        self.log(f"Look at position {target} vector {et}")

        if self.target_angle >= self.current_angle:
            ccw = self.target_angle - self.current_angle
            cw  = 360 - ccw
        else:
            cw  = self.current_angle - self.target_angle
            ccw = 360 - cw
        if ccw <= cw:
            self.direction = Rotation.CCW
            self.log(f"CCW rotation: {self.current_angle}° → {self.target_angle}°")
        else:
            self.direction = Rotation.CW
            self.log(f"CW rotation: {self.current_angle}° → {self.target_angle}°")

        # Handle the 0° == 360° aspect.
        if self.direction == Rotation.CCW:
            if self.target_angle == 0.0:
                self.target_angle = 360.0
                self.log(f"Target angle fixed: 0° → 360°")
        else: # self.direction == Rotation.CW
            if self.target_angle == 360.0:
                self.target_angle = 0.0
                self.log(f"Target angle fixed: 360° → 0°")

        if self.current_angle != self.target_angle:
            assert not self.is_done()
            EngineClock.singleton().resume(self)

    def is_done(self):
        return self.target_angle == self.current_angle

    def add_time(self, t):
        assert not self.is_done()
        new_angle      = self.current_angle + t * self.direction * self.angular_speed
        if new_angle < 0:
            pass
        i              = min(new_angle, self.current_angle)
        a              = max(new_angle, self.current_angle)
        target_crossed = i <= self.target_angle and self.target_angle <= a

        self.log(f"Adding {t} ms to rotation:")
        self.log(f"    Direction:      {self.direction}")
        self.log(f"    Angular Speed:  {self.angular_speed:.2f}°/ms")
        self.log(f"    Target Angle:   {self.target_angle:.2f}°")
        self.log(f"    Angle Jump:     {self.current_angle:.2f}° → {new_angle:.2f}°")
        self.log(f"    Target Crossed: {target_crossed}")

        if target_crossed:
            self.current_angle = self.target_angle
            assert self.is_done()
        else:
            self.current_angle = new_angle % 360

    def blit_debug(self):
        if not Config.singleton().must_log("Rotation"):
            return

        screen = Screen.singleton()
        screen.draw_vector(self.entity.position,
                           Vector2(50, 0).rotate(-self.current_angle))

        if not self.is_done():
            rect        = Rect((0, 0), (50, 50))
            rect.center = self.entity.position
            if self.direction == Rotation.CCW:
                screen.draw_arc(rect, self.current_angle, self.target_angle,
                                color=COLOR_BLUE)
            else: # self.direction == Rotation.CW
                screen.draw_arc(rect, self.target_angle, self.current_angle,
                                color=COLOR_BLUE)

            screen.draw_vector(self.entity.position,
                               Vector2(50, 0).rotate(-self.target_angle),
                               color=COLOR_BLUE)


