# from .Rotation    import Rotation
from .Translation import Translation
from .utils       import log_ex

class Physics:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    # def __init__(self, orig_angle, rotation_speed, orig_point, translation_speed):
    def __init__(self, entity, speed=0.0, angle=0, angular_speed=0):
        # self.rotation = Rotation(angle, 22.5, rotation_speed)
        self.translation = Translation(entity, speed)

    # def orientation(self):
    #     return self.rotation.current

    def target_position(self):
        return self.translation.target

    # def look_at(self, point):
    #     self.rotation.look(self.position(), point)

    def move_to(self, position):
        self.translation.move_to(position)

    def is_done(self):
        raise NotImplementedError()
        # return self.rotation.is_done() and self.translation.is_done()
        return self.translation.is_done()

    def add_time(self, t):
        # self.rotation.update()
        self.translation.add_time(t)

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
