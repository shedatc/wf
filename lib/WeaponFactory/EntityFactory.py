from .Entity import Entity
from .utils  import log_ex

class EntityFactory:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    @classmethod
    def spawn(cls, type, position):
        EntityFactory.log(f"Spawning entity:")
        EntityFactory.log(f"    Type:     {type}")
        EntityFactory.log(f"    Position: {position}")
        return Entity(type, position, speed=0.05)
