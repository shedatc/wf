from .Camera      import Camera
from .EngineClock import EngineClock
from .Screen      import Screen
from .Vector      import Vector
from .const       import DEBUG_TRANSLATION
from .utils       import log_ex

class Translation:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, entity, speed=0.0):
        self.entity = entity
        self.speed  = speed # px/ms
        self._target = None
        EngineClock.singleton().register(self)

    def move_to(self, position):
        self._target = position
        EngineClock.singleton().resume(self)

    def finish(self):
        if self._target is not None:
            self.entity.position = self._target
            self._target          = None

    def is_done(self):
        return self._target is None

    def add_time(self, t):
        if self._target is None:
            return
        assert self._target is not None, "Translation already done"

        (tx, ty)           = self._target
        (ex, ey)           = self.entity.position
        translation_vector = Vector(tx - ex, ty - ey)
        total_distance     = translation_vector.length()
        step_vector        = translation_vector.unit().scale(self.speed * t)
        step_distance      = step_vector.length()

        Translation.log(f"Adding {t} ms to translation:")
        Translation.log(f"    Translation Vector: {translation_vector}")
        Translation.log(f"    Total Distance:     {total_distance} pixels")
        Translation.log(f"    Step Vector:        {step_vector}")
        Translation.log(f"    Step Distance:      {step_distance} pixels")

        if step_distance < total_distance:
            self.entity.shift( step_vector.xy() )
            Translation.log(f"Entity {self.entity} moved to {self.entity.position}")
        else:
            self.finish()
            Translation.log(f"Entity {self.entity} stopped at {self.entity.position}")

    def blit_debug(self):
        if self._target is None:
            return
        if DEBUG_TRANSLATION:
            (x, y) = self.entity.position
            position = (x + 16, y)
            position = Camera.singleton().screen_point(position)
            (tx, ty)           = self._target
            (ex, ey)           = self.entity.position
            translation_vector = Vector(tx - ex, ty - ey)
            (vx, vy) = translation_vector.xy()
            Screen.singleton().text(f"V: ({vx:.2f}, {vy:.2f})", position)

