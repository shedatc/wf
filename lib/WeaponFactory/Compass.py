from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid              import Grid
from pathfinding.finder.finder          import ExecutionTimeException

from .utils  import log_ex

# A compass help find a navigation path through an arena, avoiding obstacles.
class Compass:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

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
