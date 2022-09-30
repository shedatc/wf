from .animation import AnimationManager
from .resources import Resources
from .sprites   import Entity
from .utils     import Config, log_ex

class Drone(Entity):

    def log(msg):
        log_ex(msg, category="Drone")

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
