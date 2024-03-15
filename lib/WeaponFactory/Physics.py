# Units:
#    Speed: frames per seconds

from .Rotation    import Rotation
from .Translation import Translation
from .utils       import log_ex

class Physics:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, orig_angle, rotation_speed, orig_point, translation_speed):
        self.rotation    = Rotation(orig_angle, 22.5, rotation_speed)
        self.translation = Translation(orig_point, translation_speed)

    def show(self):
        Physics.log(f"Position:    {self.position()}")
        Physics.log(f"Orientation: {self.orientation()}")
        Physics.log(f"Rotating:    {not self.rotation.is_done()}")
        Physics.log(f"Translating: {not self.translation.is_done()}")

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
