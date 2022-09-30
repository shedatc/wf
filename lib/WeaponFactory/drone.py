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

    def init_animation(self):
        self.animation = DroneAnimationManager()

    def update_animation(self):
        o = str(self.physics.orientation())
        if o[-2:] == '.0':
            o = o[:-2]
        self.animation.select(f"standby@{o}")
        self.animation.resume()
        self.animation.update()

class DroneAnimationManager(AnimationManager):

    # FIXME Must use assets/sprites/drone/drone.json
    def __init__(self):
        AnimationManager.__init__(self, Resources.singleton().image("drone"))
        self.add("standby@0", [
            (0, 0),
        ])
        self.add("standby@22.5", [
            (8, 0),
        ])
        self.add("standby@45", [
            (16, 0),
        ])
        self.add("standby@67.5", [
            (24, 0),
        ])
        self.add("standby@90", [
            (32, 0),
        ])
        self.add("standby@112.5", [
            (40, 0),
        ])
        self.add("standby@135", [
            (48, 0),
        ])
        self.add("standby@157.5", [
            (56, 0),
        ])
        self.add("standby@180", [
            (64, 0),
        ])
        self.add("standby@202.5", [
            (72, 0),
        ])
        self.add("standby@225", [
            (80, 0),
        ])
        self.add("standby@247.5", [
            (88, 0),
        ])
        self.add("standby@270", [
            (96, 0),
        ])
        self.add("standby@292.5", [
            (104, 0),
        ])
        self.add("standby@315", [
            (112, 0),
        ])
        self.add("standby@337.5", [
            (120, 0),
        ])
        self.add("left_rotation", [
            (0, 0),
            (8, 0),
            (16, 0),
            (24, 0),
            (32, 0),
            (40, 0),
            (48, 0),
            (56, 0),
            (64, 0),
            (72, 0),
            (80, 0),
            (88, 0),
            (96, 0),
            (104, 0),
            (112, 0),
            (120, 0),
        ])
        self.add("right_rotation", [
            (0, 0),
            (120, 0),
            (112, 0),
            (104, 0),
            (96, 0),
            (88, 0),
            (80, 0),
            (72, 0),
            (64, 0),
            (56, 0),
            (48, 0),
            (40, 0),
            (32, 0),
            (24, 0),
            (16, 0),
            (8, 0),
        ])
        self.select("standby@0")
        self.resume()
