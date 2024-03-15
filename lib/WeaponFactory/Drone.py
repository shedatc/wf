from .Entity import Entity
from .utils  import log_ex

class Drone(Entity):

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, square):
        Drone.log(f'square={square}')
        Entity.__init__(self, "drone", square.point(), 8, 8, 22.5, 10, 10)

    def update_animation(self):
        o = str(self.physics.orientation())
        if o[-2:] == '.0':
            o = o[:-2]
        self.animation.select(f"standby@{o}")
        self.animation.resume()
        self.animation.update()
