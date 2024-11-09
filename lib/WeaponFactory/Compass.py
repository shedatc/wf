from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid              import Grid
from pathfinding.finder.a_star          import AStarFinder
from pathfinding.finder.finder          import ExecutionTimeException

from .Config import Config
from .utils  import log_ex

# The compass help find a navigation path through an arena, avoiding obstacles.
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

        config     = Config.singleton().load("compass.json")
        time_limit = config["time_limit"]

        self.grid   = Grid(matrix=obstacles_matrix)
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always,
                                  time_limit=time_limit)
        Compass.log(f"Finder: {self.finder.__class__}")

        Compass._singleton = self

    def change(self, square, walkable):
        (x, y) = square
        self.grid.node(x, y).walkable = walkable
        if walkable:
            Compass.log(f"[{x}, {y}] is now walkable")
        else:
            Compass.log(f"[{x}, {y}] is now an obstacle")

    def is_obstacle(self, square):
        (x, y) = square
        try:
            n = self.grid.node(x, y)
        except IndexError:
            Compass.log(f"No node at [{x}, {y}]")
            raise
        return n.walkable is False

    def _is_next_to(self, a, b):
        (ax, ay) = a
        (bx, by) = b
        dx       = abs(ax - bx)
        dy       = abs(ay - by)
        return dx <= 1 and dy <= 1

    def find_path(self, from_square, to_square):
        assert from_square != to_square

        Compass.log(f"Cleanup grid…")
        self.grid.cleanup()
        Compass.log(f"Grid clean")

        (fx, fy) = from_square
        (tx, ty) = to_square
        from_node = self.grid.node(fx, fy)
        to_node   = self.grid.node(tx, ty)

        Compass.log(f"Finding path: [{fx}, {fy}] → [{tx}, {ty}]")
        try:
            (hops, runs) = self.finder.find_path(from_node, to_node, self.grid)
        except ExecutionTimeException:
            Compass.log(f"No path found: time out")
            return None
        else:
            Compass.log(f"Path found in {runs} runs: {len(hops)} hops")
        if len(hops) < 2:
            Compass.log(f"No path found: not enough hops")
            return None
        assert len(hops) > 1
        assert hops[ 0] == from_square
        assert hops[-1] == to_square

        hops.pop(0) # Remove the entity's current position.

        # Ensure each hop directly follow its predecessor.
        if False:
            previous_hop = from_square
            for h in range(len(hops)):
                current_hop  = hops[h]
                assert self._is_next_to(current_hop, previous_hop)
                hops[h]      = current_hop
                previous_hop = current_hop

        return hops
