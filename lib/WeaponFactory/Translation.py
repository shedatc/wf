from pygame.math import Vector2

from .Config      import Config
from .EngineClock import EngineClock
from .Screen      import Screen
from .colors      import COLOR_RED
from .utils       import log_ex

class Translation:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, entity, speed=0.0):
        self.entity          = entity
        self.speed           = speed # px/ms
        self.target_position = entity.position
        EngineClock.singleton().register(self)

        self.debug_step_vectors = []

    def move_to(self, position):
        self.target_position = position
        EngineClock.singleton().resume(self)

        self.debug_orig_position = self.entity.position
        self.debug_step_vectors.clear()

    def is_done(self):
        return self.entity.position == self.target_position

    def add_time(self, t):
        assert not self.is_done()

        (tx, ty)           = self.target_position
        (ex, ey)           = self.entity.position
        translation_vector = Vector2(tx - ex, ty - ey)
        total_distance     = translation_vector.length()
        step_vector        = (translation_vector / total_distance) * (self.speed * t)
        step_distance      = step_vector.length()

        Translation.log(f"Adding {t} ms to translation:")
        Translation.log(f"    Translation Vector: {translation_vector}")
        Translation.log(f"    Total Distance:     {total_distance} px")
        Translation.log(f"    Step Vector:        {step_vector}")
        Translation.log(f"    Step Distance:      {step_distance} px")

        if step_distance < total_distance:
            self.entity.shift( step_vector.xy )
            Translation.log(f"Entity {self.entity} moved to {self.entity.position}")
            self.debug_step_vectors.append(step_vector)
        else:
            self.entity.position = self.target_position
            Translation.log(f"Entity {self.entity} stopped at {self.entity.position}")
            self.debug_step_vectors.clear()

    def blit_debug(self):
        if not Config.singleton().must_log("Translation"):
            return

        if self.target_position == self.entity.position:
            return

        screen = Screen.singleton()
        p      = self.debug_orig_position
        for step_vector in self.debug_step_vectors:
            screen.draw_vector(p, step_vector, color=COLOR_RED)
            p += step_vector
        screen.draw_point(self.target_position)
