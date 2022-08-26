import pyxel

# Path Finding:
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid              import Grid

from math import sqrt

from .const import SQUARE_SIZE
from .utils import Config, logEx

# A compass help find a navigation path through an arena, avoiding obstacles.
class Compass:

    singleton = None

    def getSingleton():
        assert Compass.singleton is not None
        return Compass.singleton

    def log(msg):
        logEx(msg, category="Compass")

    def __init__(self, obstaclesMatrix):
        assert Compass.singleton is None
        Compass.singleton = self

        self.grid = Grid(matrix=obstaclesMatrix)

        from pathfinding.finder.a_star import AStarFinder
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always,
                                  time_limit=1)
        Compass.log(f"Finder: {self.finder.__class__}")

    def setWalkable(self, square):
        self.grid.node(square.u, square.v).walkable = True

    def setObstacle(self, square):
        self.grid.node(square.u, square.v).walkable = False

    def isObstacle(self, square):
        return self.grid.node(square.u, square.v).walkable == False

    def navigate(self, entity, square):
        if entity.isMoving():
            entitySquare = entity.targetPosition().square()
        else:
            entitySquare = entity.position().square()
        Compass.log(f"Navigate {entity.name} from {entitySquare} to {square}")

        Compass.log(f"Cleanup grid…")
        self.grid.cleanup()
        Compass.log(f"Grid clean")

        start        = self.grid.node(entitySquare.u, entitySquare.v)
        end          = self.grid.node(square.u, square.v)

        Compass.log(f"Finding path…")
        (hops, runs) = self.finder.find_path(start, end, self.grid)
        Compass.log(f"Path found")

        Compass.log(f"steps={len(hops)} runs={runs} hops={hops}")

        def squarify(hop):
            (u, v) = hop
            from .arena import Square
            return Square(u, v)

        if hops != []:
            # Remove the entity's current position.
            firstHop = squarify( hops.pop(0) )
            assert firstHop == entitySquare

        if hops != []:
            previousHop = entitySquare
            for h in range(len(hops)):
                currentHop  = squarify(hops[h])
                assert currentHop.isNextTo(previousHop)
                hops[h]     = currentHop
                previousHop = currentHop
            entity.navigate(hops)
        else:
            Compass.log("Invalid navigation path")

# A navigation path is a list of hops. A hop is a square directly connected to
# the previous one.
class NavPath:

    def __init__(self, entity):
        self.entity = entity
        self.hop    = None
        self.hops   = []
        self.show()

    def log(self, msg):
        logEx(msg, name=self.entity.name, category="NavPath")

    def clear(self):
        self.hop  = None
        self.hops = []

    def set(self, hops):
        assert len(hops) >= 1
        self.hop  = hops[0]
        self.hops = hops[1:]
        self.show()

    def nextHop(self):
        if len(self.hops) >= 1:
            self.hop  = self.hops[0]
            self.hops = self.hops[1:]

            c = Compass.getSingleton()
            if c.isObstacle(self.hop):
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
        assert not self.isDone()
        if len(self.hops) >= 1:
            return self.hops[-1]
        elif self.hop is not None:
            return self.hop

    def isDone(self):
        return self.hop is None

    def show(self):
        hops = "[" + ", ".join([str(h) for h in self.hops]) + "]"
        self.log(f"hop={self.hop} hops={hops}")

    def drawNextHop(self, hop):
        if not hop.isVisible():
            return
        p = hop.point().screen()
        pyxel.circ(p.x, p.y, 1, pyxel.COLOR_LIGHT_BLUE)

    def drawHop(self, hop):
        if not hop.isVisible():
            return
        p = hop.point().screen()
        pyxel.rect(p.x - 1, p.y - 1,
                   2, 2, pyxel.COLOR_LIGHT_BLUE)

    def drawLastHop(self, hop):
        if not hop.isVisible():
            return
        p = hop.point().screen()
        pyxel.circ(p.x, p.y,
                   2, pyxel.COLOR_LIGHT_BLUE)

    def draw(self):
        if self.isDone():
            return
        if len(self.hops) >= 1:
            self.drawNextHop(self.hop)
            for hop in self.hops[0:-1]:
                self.drawHop(hop)
            hop = self.hops[-1]
            self.drawLastHop(hop)
        else:
            self.drawLastHop(self.hop)

# A navigation beacon is a square in the arena that is not an obstacle.
class NavBeacon:

    def log(msg):
        logEx(msg, category="NavBeacon")

    def __init__(self):
        from .arena import Square
        self.square    = Square(0, 0)
        self.isEnabled = False

    def tryMove(self, square):
        if square.isObstacle():
            self.square    = None
            self.isEnabled = False
            NavBeacon.log(f"Square {square}, point {square.point()} is an obstacle")
        else:
            self.square    = square
            self.isEnabled = True
            NavBeacon.log(f"Moved to square {square}, point {square.point()}")
        return self.isEnabled

    def fromMouse(self):
        from .arena import Square
        square = Square(0, 0).fromMouse()
        self.tryMove(square)
        return self

    def __str__(self):
        return str(self.square)
