import pyxel

from .const      import OBSTACLE, SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIZE, WALKABLE
from .input      import Mouse
from .navigation import Compass
from .utils      import Config, logEx

class Camera:

    singleton = None

    def getSingleton():
        if Camera.singleton is None:
            Camera.singleton = Camera()
        return Camera.singleton

    def log(msg):
        logEx(msg, category="Camera")

    def __init__(self):
        assert Camera.singleton is None
        Camera.singleton = self

        a           = Arena.getSingleton()
        self.u      = 0
        self.v      = 0
        self.width  = 32
        self.height = 32
        self.lu     = a.width  - self.width  - 1
        self.lv     = a.height - self.height - 1
        self.show()

    def show(self):
        Camera.log(f"u={self.u} v={self.v}")
        Camera.log(f"lu={self.lu} lv={self.lv}")
        Camera.log(f"width={self.width} height={self.height}")

    def left(self):
        Camera.log(f"left")
        if self.u >= 1:
            self.u -= 1

    def right(self):
        Camera.log(f"right")
        if self.u <= self.lu:
            self.u += 1

    def up(self):
        Camera.log(f"up")
        if self.v >= 1:
            self.v -= 1

    def down(self):
        Camera.log(f"down")
        if self.v <= self.lv:
            self.v += 1

    def move(self, u, v):
        self.u = min(SCREEN_WIDTH  - self.width,  max(0, u))
        self.v = min(SCREEN_HEIGHT - self.height, max(0, v))

    def centeredMove(self, u, v):
        self.move(u - self.width  // 2,
                  v - self.height // 2)

    def view(self, square):
        assert isinstance(square, Square)
        return self.u <= square.u and square.u <= self.u + self.width \
            and self.v <= square.v and square.v <= self.v + self.height

# An arena is the terrain with all its obstacles.
class Arena:

    singleton = None

    def getSingleton():
        assert Arena.singleton is not None
        return Arena.singleton

    def log(msg):
        logEx(msg, category="Arena")

    def logEntitiesMatrix(self):
        if not Config.mustLog("Arena"):
            return
        Arena.log(f"Entities Matrix:")
        for v in range(self.height):
            for u in range(self.width):
                    entities = self.entitiesMatrix[v][u]
                    if len(entities) >= 1:
                        msg = f"[{u}, {v}]"
                        for entity in entities:
                            msg += f" {entity.name}"
                        Arena.log(msg)

    def logObstaclesMatrix(self):
        if not Config.mustLog("Arena"):
            return
        Arena.log(f"Obstacles Matrix:")
        for v in range(self.height):
            msg = ''
            for u in range(self.width):
                    if self.obstaclesMatrix[v][u] == OBSTACLE:
                        msg += 'x'
                    else:
                        msg += ' '
            Arena.log(msg)

    def __init__(self, config):
        assert Arena.singleton is None
        Arena.singleton = self

        Arena.log(f"square={SQUARE_SIZE}")

        self.tm     = 0
        self.width  = pyxel.tilemap(self.tm).width
        self.height = pyxel.tilemap(self.tm).height
        Arena.log(f"tm={self.tm} size={self.width}x{self.height}")

        # Obstacles:
        o = config["obstacles"]["operator"] or "in"
        l = config["obstacles"]["list"]
        assert o in ["in", "not-in"], "unknown obstacles operator"
        if o == "in":
            def isTileObstacle(data):
                return data in l
        elif o == "not-in":
            def isTileObstacle(data):
                return data not in l

        self.obstaclesMatrix = [[1] * self.width for i in range(self.height)]
        for v in range(self.height):
            msg = ''
            for u in range(self.width):
                tileData = pyxel.tilemap(self.tm).pget(u, v)
                tileData = (tileData[0] * SQUARE_SIZE, tileData[1] * SQUARE_SIZE) # Match what's displayed when hovering tiles in editor.
                tileData = str(tileData)
                if isTileObstacle(tileData):
                    self.obstaclesMatrix[v][u] = OBSTACLE
                else:
                    self.obstaclesMatrix[v][u] = WALKABLE
        # self.logObstaclesMatrix()

        self.entitiesMatrix = [[1] * self.width for i in range(self.height)]
        for v in range(self.height):
            for u in range(self.width):
                    self.entitiesMatrix[v][u] = []
        self.logEntitiesMatrix()

    def tileDataFromMouse(self):
        return Square(0, 0).fromMouse().tileData()

    def isObstacle(self, square):
        return self.obstaclesMatrix[square.v][square.u] == OBSTACLE

    def entitiesAtSquare(self, u, v):
        return self.entitiesMatrix[v][u]

    def notify(self, event, observable, **kwargs):
        if event == "entity-spawned":
            self.entitySpawned(observable, kwargs["square"])
        elif event == "entity-moved":
            self.entityMoved(observable, kwargs["oldSquare"], kwargs["newSquare"])
        else:
            raise AssertionError(f"Event not supported: {event}")

    def entitySpawned(self, entity, square):
        Arena.log(f"Entity {entity.name} spawned on {square}")

        (u, v) = (square.u, square.v)
        self.entitiesMatrix[v][u].append(entity)
        self.obstaclesMatrix[v][u] = OBSTACLE
        Compass.getSingleton().setObstacle(square)
        Arena.log(f"Obstacle at square {square}")
        self.logEntitiesMatrix()

    def entityMoved(self, entity, oldSquare, newSquare):
        Arena.log(f"Entity {entity.name} moved from {oldSquare} to {newSquare}")

        (ou, ov) = (oldSquare.u, oldSquare.v)
        self.entitiesMatrix[ov][ou].remove(entity)
        if (len(self.entitiesMatrix[ov][ou]) == 0):
            self.obstaclesMatrix[ov][ou] = WALKABLE
            Compass.getSingleton().setWalkable(oldSquare)
            Arena.log(f"No more obstacle at square {oldSquare}")

        (nu, nv) = (newSquare.u, newSquare.v)
        self.entitiesMatrix[nv][nu].append(entity)
        assert len(self.entitiesMatrix[nv][nu]) == 1, "Stacking not allowed for now"

        self.obstaclesMatrix[nv][nu] = OBSTACLE
        Compass.getSingleton().setObstacle(newSquare)
        Arena.log(f"Obstacle at square {newSquare}")
        self.logEntitiesMatrix()

class ArenaView:

    singleton = None

    def getSingleton():
        if ArenaView.singleton is None:
            ArenaView.singleton = ArenaView()
        return ArenaView.singleton

    def log(msg):
        logEx(msg, category="ArenaView")

    def __init__(self):
        self.isTactical = True
        self.svi        = 2 # Strategic View Image

        ArenaView.log(f"isTactical={self.isTactical} svi={self.svi}")

    def getWidth(self):
        return Arena.getSingleton().width

    def getHeight(self):
        return Arena.getSingleton().height

    def getTilemap(self):
        return Arena.getSingleton().tm

    def tactical(self):
        self.isTactical = True
        return self

    def strategic(self):
        self.isTactical = False
        return self

    def toggle(self):
        self.isTactical = not self.isTactical
        return self

    def update(self):
        if self.isTactical:
            Region.getSingleton().update()

    def drawTactical(self):
        c = Camera.getSingleton()
        pyxel.bltm(0, 0,                                              # x, y
                   self.getTilemap(),                                 # tm
                   c.u * SQUARE_SIZE, c.v * SQUARE_SIZE,              # u, v
                   c.width * SQUARE_SIZE, c.height * SQUARE_SIZE,     # w, h
                   0)                                                 # colkey
        Region.getSingleton().draw()

    def drawStrategic(self):
        c = Camera.getSingleton()
        pyxel.blt(0, 0, self.svi, 0, 0, self.getWidth(), self.getHeight())
        for v in range(0, SCREEN_HEIGHT):
            for u in range(0, SCREEN_WIDTH):
                entities = Arena.getSingleton().entitiesAtSquare(u, v)
                if len(entities) >= 1:
                    for e in entities:
                        if e.isSelected:
                            pyxel.pset(u, v, 9)
                        else:
                            pyxel.pset(u, v, 13)
            pyxel.rectb(c.u, c.v, c.width, c.height, 12)

    def draw(self):
        if self.isTactical:
            self.drawTactical()
        else:
            self.drawStrategic()

# A point somewhere in the arena.
# A point is said to be visible if in the camera range.
class Point:

    def log(msg):
        logEx(msg, category="Point")

    def __init__(self, x, y):
        assert 0 <= x and x <= SCREEN_WIDTH*SQUARE_SIZE-1
        assert 0 <= y and y <= SCREEN_HEIGHT*SQUARE_SIZE-1
        (self.x, self.y) = (x, y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, otherPoint):
        return self.x == otherPoint.x and self.y == otherPoint.y

    # Return the square containing the point.
    def square(self):
        return Square(self.x // SQUARE_SIZE, self.y // SQUARE_SIZE)

    # Return the point in screen coordinates.
    def screen(self):
        assert self.isVisible()
        c = Camera.getSingleton()
        return Point(self.x - (c.u * SQUARE_SIZE),
                     self.y - (c.v * SQUARE_SIZE))

    # Move to the coordinates pointed by the mouse.
    def fromMouse(self):
        (mx, my) = Mouse.getCoords()
        c        = Camera.getSingleton()
        self.x   = c.u * SQUARE_SIZE + mx
        self.y   = c.v * SQUARE_SIZE + my
        return self

    # Tell if the point is visible from current camera's position.
    def isVisible(self):
        return self.square().isVisible()

# A square in the arena.
class Square:

    def log(msg):
        logEx(msg, category="Square")

    def __init__(self, u, v):
        u = int(u)
        v = int(v)
        assert 0 <= u and u <= SCREEN_WIDTH-1
        assert 0 <= v and v <= SCREEN_HEIGHT-1

        (self.u, self.v)   = (u, v)
        (self.pu, self.pv) = (None, None)
        self.tm            = Arena.getSingleton().tm

    def __str__(self):
        return f"[{self.u}, {self.v}]"

    def __eq__(self, otherSquare):
        return self.u == otherSquare.u and self.v == otherSquare.v

    def move(self, u, v):
        (self.pu, self.pv) = (self.u, self.v)
        (self.u, self.v)   = (u, v)
        return self

    def relativeMove(self, u, v):
        c = Camera.getSingleton()
        return self.move(c.u + u, c.v + v)

    def canRollback(self):
        return self.pu is not None and self.pv is not None

    def rollback(self):
        assert self.canRollback()
        (self.u, self.v)   = (self.pu, self.pv)
        (self.pu, self.pv) = (None, None)
        return self

    def fromMouse(self):
        (mx, my) = Mouse.getCoords()
        (mu, mv) = (mx // SQUARE_SIZE, my // SQUARE_SIZE)
        self.relativeMove(mu, mv)
        return self

    def tileData(self):
        return pyxel.tilemap(self.tm).get(self.u, self.v)

    def isObstacle(self):
        return Arena.getSingleton().isObstacle(self)

    def isVisible(self):
        return Camera.getSingleton().view(self)

    def point(self):
        return Point(self.u * SQUARE_SIZE + SQUARE_SIZE // 2,
                     self.v * SQUARE_SIZE + SQUARE_SIZE // 2)

    # Tell if the other square is next to this one. A square is considered next
    # to itself.
    def isNextTo(self, otherSquare):
        du = abs(self.u - otherSquare.u)
        dv = abs(self.v - otherSquare.v)
        return du <= 1 and dv <= 1

class Region:

    singleton = None

    def getSingleton():
        if Region.singleton is None:
            Region.singleton = Region()
        return Region.singleton

    def log(msg):
        logEx(msg, category="Region")

    def __init__(self):
        assert Region.singleton is None
        Region.singleton = self

        self.start     = None
        self.end       = None
        self.isEnabled = False
        Region.log(f"start={self.start} end={self.end} isEnabled={self.isEnabled}")

    def enable(self):
        if self.isEnabled:
            Region.log("already enabled")
        else:
            self.start     = Square(0, 0).fromMouse()
            self.end       = Square(0, 0).fromMouse()
            self.isEnabled = True
            Region.log("enabled")

    def disable(self):
        if self.isEnabled:
            Region.log("disabled")
            entities       = self.getEntities()
            self.start     = None
            self.end       = None
            self.isEnabled = False
            return entities
        else:
            Region.log("already disabled")
            return None

    def isEmpty(self):
        self.end is None or self.start == self.end

    def update(self):
        if not self.isEnabled:
            return
        if self.end is not None:
            self.end.fromMouse()
            Region.log(f"start={self.start} end={self.end} isEnabled={self.isEnabled}")

    def getOrigin(self):
        assert self.isEnabled
        s = self.start
        e = self.end
        u = min(s.u, e.u)
        v = min(s.v, e.v)
        return Square(u, v)

    def getWidth(self):
        assert self.isEnabled
        return abs(self.start.u - self.end.u) + 1

    def getHeight(self):
        assert self.isEnabled
        return abs(self.start.v - self.end.v) + 1

    def draw(self):
        if not self.isEnabled:
            return

        # Draw the square-level region
        o  = self.getOrigin().point().screen()
        hs = SQUARE_SIZE // 2
        Region.log(f"origin={o}")
        pyxel.rectb(o.x - hs, o.y - hs,
                    self.getWidth() * SQUARE_SIZE, self.getHeight() * SQUARE_SIZE,
                    8)

    # Return the entities that are part of the region.
    def getEntities(self):
        entities = []
        o = self.getOrigin()
        a = Arena.getSingleton()
        for v in range(o.v, o.v + self.getHeight()):
            for u in range(o.u, o.u + self.getWidth()):
                e = a.entitiesAtSquare(u, v)
                Region.log(f"e={e} len(e)={len(e)}")
                if len(e) >= 1:
                    # If at least one entity is on the square, add only the
                    # first one to handle stacking.
                    entities.append(e[0])
        Region.log(f"entities={entities}")
        return entities

