from .Config      import Config
from .Rotation    import Rotation
from .Translation import Translation
from .utils       import log_ex

class Physics:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, entity, speed=0.0, orig_angle=0.0, angular_speed=0.0):
        self._entity      = entity
        self._translation = Translation(entity, speed)
        self._rotation    = Rotation(entity, orig_angle, angular_speed)

    def orientation(self):
        return self._rotation.current_angle

    def target_position(self):
        return self._translation.target_position

    def look_at(self, point):
        self._rotation.look_at(point)

    def move_to(self, position):
        self._translation.move_to(position)

    def is_translating(self):
        return not self._translation.is_done()

    def is_rotating(self):
        return not self._rotation.is_done()

    def is_done(self):
        return self._translation.is_done() and self._rotation.is_done()

    def blit_debug(self):
        if not Config.singleton().must_log("Physics"):
            return
        self._translation.blit_debug()
        self._rotation.blit_debug()
