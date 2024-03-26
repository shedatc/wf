from .EngineClock import EngineClock
from .Entity      import Entity
from .utils       import log_ex

class EntityFactory:

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
        self._singleton = self

    def spawn(type, position):
        EntityFactory.log(f"Spawning entity:")
        EntityFactory.log(f"    Type:     {type}")
        EntityFactory.log(f"    Position: {position}")
        return Entity(type, position, speed=0.05)
