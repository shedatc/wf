from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid              import Grid
from pathfinding.finder.a_star          import AStarFinder
from pathfinding.finder.finder          import ExecutionTimeException

from .utils import log_ex

# A compass help find a navigation path through an arena, avoiding obstacles.
class Compass:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def delete_singleton(cls):
        cls._singleton = None

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, obstacles_matrix):
        assert Compass._singleton is None

        # FIXME Make time_limit configurable
        self.grid   = Grid(matrix=obstacles_matrix)
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always,
                                  time_limit=0.5)
        Compass.log(f"Finder: {self.finder.__class__}")

        Compass._singleton = self

    def set_walkable(self, square):
        (x, y) = square
        self.grid.node(x, y).walkable = True

    def set_obstacle(self, square):
        (x, y) = square
        self.grid.node(x, y).walkable = False

    def is_obstacle(self, square):
        (x, y) = square
        try:
            n = self.grid.node(x, y)
        except IndexError:
            Compass.log(f"No node at ({x}, {y})")
            raise
        return n.walkable is False

    def is_next_to(self, a, b):
        (ax, ay) = a
        (bx, by) = b
        dx       = abs(ax - bx)
        dy       = abs(ay - by)
        return dx <= 1 and dy <= 1

    def find_path(self, from_square, to_square):
        Compass.log(f"Cleanup grid…")
        self.grid.cleanup()
        Compass.log(f"Grid clean")

        (fx, fy) = from_square
        (tx, ty) = to_square
        from_node = self.grid.node(fx, fy)
        to_node   = self.grid.node(tx, ty)

        Compass.log(f"Finding path…")
        try:
            (hops, runs) = self.finder.find_path(from_node, to_node, self.grid)
        except ExecutionTimeException:
            Compass.log(f"No path found")
            return None
        else:
            Compass.log(f"Path found")

        Compass.log(f"steps={len(hops)} runs={runs} hops={hops}")

        if hops != []:
            # Remove the entity's current position.
            firstHop = hops.pop(0)
            assert firstHop == from_square

        if hops == []:
            Compass.log("Invalid path")
            return None

        previous_hop = from_square
        for h in range(len(hops)):
            current_hop  = hops[h]
            assert self.is_next_to(current_hop, previous_hop)
            hops[h]      = current_hop
            previous_hop = current_hop
        return hops
