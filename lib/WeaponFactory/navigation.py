import pygame

from pygame import Rect

# Path Finding:
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid              import Grid
from pathfinding.finder.finder          import ExecutionTimeException

from math import sqrt

from .const import SQUARE_SIZE
from .utils import Config, log_ex

# A compass help find a navigation path through an arena, avoiding obstacles.
class Compass:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    def log(msg):
        log_ex(msg, category="Compass")

    def __init__(self, obstacles_matrix):
        assert Compass._singleton is None
        Compass._singleton = self
        self.grid          = Grid(matrix=obstacles_matrix)

        from pathfinding.finder.a_star import AStarFinder
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always,
                                  time_limit=0.5)
        Compass.log(f"Finder: {self.finder.__class__}")

    def set_walkable(self, square):
        self.grid.node(square.u, square.v).walkable = True

    def set_obstacle(self, square):
        self.grid.node(square.u, square.v).walkable = False

    def is_obstacle(self, square):
        return self.grid.node(square.u, square.v).walkable == False

    def navigate(self, entity, square):
        if entity.is_moving():
            entity_square = entity.target_position().square()
        else:
            entity_square = entity.position().square()
        Compass.log(f"Navigate {entity.name} from {entity_square} to {square}")

        Compass.log(f"Cleanup grid…")
        self.grid.cleanup()
        Compass.log(f"Grid clean")

        start = self.grid.node(entity_square.u, entity_square.v)
        end   = self.grid.node(square.u, square.v)

        Compass.log(f"Finding path…")
        try:
            (hops, runs) = self.finder.find_path(start, end, self.grid)
        except ExecutionTimeException:
            Compass.log(f"No path found")
            entity.stop()
            return False
        else:
            Compass.log(f"Path found")

        Compass.log(f"steps={len(hops)} runs={runs} hops={hops}")

        def squarify(hop):
            (u, v) = hop
            from .arena import Square
            return Square(u, v)

        if hops != []:
            # Remove the entity's current position.
            firstHop = squarify( hops.pop(0) )
            assert firstHop == entity_square

        if hops == []:
            Compass.log("Invalid path")
            return False

        previous_hop = entity_square
        for h in range(len(hops)):
            current_hop  = squarify(hops[h])
            assert current_hop.is_next_to(previous_hop)
            hops[h]      = current_hop
            previous_hop = current_hop
        entity.navigate(hops)
        return True

# A navigation path is a list of hops. A hop is a square directly connected to
# the previous one.
class NavPath:

    def __init__(self, entity):
        self.entity = entity
        self.hop    = None
        self.hops   = []
        self.show()

    def log(self, msg):
        log_ex(msg, name=self.entity.name, category="NavPath")

    def clear(self):
        self.hop  = None
        self.hops = []

    def set(self, hops):
        assert len(hops) >= 1
        self.hop  = hops[0]
        self.hops = hops[1:]
        self.show()

    def next_hop(self):
        if len(self.hops) >= 1:
            self.hop  = self.hops[0]
            self.hops = self.hops[1:]

            c = Compass.singleton()
            if c.is_obstacle(self.hop):
                if len(self.hops) == 0:
                    self.log(f"Obstacle at destination {self.hop}")
                    self.log(f"Stop here")
                    self.hop  = None
                    self.hops = []
                else:
                    self.log(f"Obstacle at next hop {self.hop}")
                    self.log(f"Renavigate")
                    c.navigate(self.entity, self.destination())
        else:
            self.log(f"Done")
            self.hop  = None
            self.hops = []

    def destination(self):
        assert not self.is_done()
        if len(self.hops) >= 1:
            return self.hops[-1]
        elif self.hop is not None:
            return self.hop

    def is_done(self):
        return self.hop is None

    def show(self):
        hops = "[" + ", ".join([str(h) for h in self.hops]) + "]"
        self.log(f"hop={self.hop} hops={hops}")

    def blit_next_hop(self, surface, hop):
        if not hop.is_visible():
            return
        p = hop.point().screen()

        pygame.draw.rect(surface, (0, 0, 200),
                         Rect((p.x-2, p.y-2), (4, 4)))

    def blit_hop(self, surface, hop):
        if not hop.is_visible():
            return
        p = hop.point().screen()

        pygame.draw.rect(surface, (0, 0, 200),
                         Rect((p.x-1, p.y-1), (2, 2)))

    def blit_last_hop(self, surface, hop):
        if not hop.is_visible():
            return
        p = hop.point().screen()

        pygame.draw.rect(surface, (0, 0, 200),
                         Rect((p.x-2, p.y-2), (4, 4)))

    def blit(self, surface):
        if self.is_done():
            return
        if len(self.hops) >= 1:
            self.blit_next_hop(surface, self.hop)
            for hop in self.hops[0:-1]:
                self.blit_hop(surface, hop)
            hop = self.hops[-1]
            self.blit_last_hop(surface, hop)
        else:
            self.blit_last_hop(surface, self.hop)

# A navigation beacon is a square in the arena that is not an obstacle.
class NavBeacon:

    def log(msg):
        log_ex(msg, category="NavBeacon")

    def __init__(self):
        from .arena import Square
        self.square     = Square(0, 0)
        self.is_enabled = False

    def try_move(self, square):
        if square.is_obstacle():
            self.square     = None
            self.is_enabled = False
            NavBeacon.log(f"Square {square}, point {square.point()} is an obstacle")
        else:
            self.square     = square
            self.is_enabled = True
            NavBeacon.log(f"Moved to square {square}, point {square.point()}")
        return self.is_enabled

    def from_mouse(self):
        from .arena import Square
        square = Square(0, 0).from_mouse()
        self.try_move(square)
        return self

    def __str__(self):
        return str(self.square)
