from .Entity        import Entity
from .SpriteFactory import SpriteFactory
from .StatCounter   import StatCounter
from .utils         import log_ex

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
        self.entity_count = StatCounter()

    def spawn(self, type, position):
        EntityFactory.log(f"Spawning entity:")
        EntityFactory.log(f"    Type:     {type}")
        EntityFactory.log(f"    Position: {position}")
        e = Entity(type, position)
        self.entity_count += 1

        # Entities are sprites too, so notify their factory.
        SpriteFactory.singleton().add_sprite(e)

        return e
