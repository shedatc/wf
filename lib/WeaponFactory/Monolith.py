from .Entity  import Entity
from .Physics import Physics

class Monolith(Entity):

    def __init__(self, position):
        Entity.__init__(self, "monolith-0", position,
                        speed=0.05)
