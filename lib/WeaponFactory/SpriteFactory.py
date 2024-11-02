from .StatCounter import StatCounter
from .utils       import log_ex

class SpriteFactory:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        self.sprites      = []
        self.sprite_count = StatCounter()

    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        self.sprite_count += 1
