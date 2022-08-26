import pyxel

from .animation  import Animation, AnimationManager
from .arena      import Arena
from .navigation import Compass, NavPath
from .physics    import Physics
from .resources  import Resources
from .utils      import Config, Observable, logEx

# A sprite is something that is animated.
#
# A sprite's coordinates are expressed in pixels (via its `point` property, of
# type Point). There's no direct relationship between a sprite and a square.
class Sprite:

    def __init__(self, name, origPoint, width, height):
        self.img    = Resources.image(name)
        self.name   = f"{name}@{hex(id(self))}"
        self.point  = origPoint
        self.width  = width
        self.height = height

        self.initAnimation(self.img)
        assert isinstance(self.animation, AnimationManager)

        Sprite.log(self, f'point={origPoint} size={width}x{height}')

    def log(self, msg):
        logEx(msg, category="Sprite", name=self.name)

    def position(self):
        return self.point

    def initAnimation(self, img):
        raise NotImplementedError

    def update(self):
        self.updateAnimation()

    def updateAnimation(self):
        self.animation.update()

    def isVisible(self):
        return self.position().isVisible()

    def draw(self):
        if not self.isVisible():
            return

        p = self.position().screen()
        self.animation.drawAt(p.x, p.y)

        if Config.mustLog("Sprite"):
            pyxel.text(p.x + 5, p.y, self.name, 0)

# An entity is a sprite that somehow obey the laws of physics.
#
# There's a relationship between the entity and squares via the navigation
# system (see `NavPath`).
class Entity(Sprite, Observable):

    def __init__(self, name, origPoint, width, height, rotStep, rotFps, trFps):
        Sprite.__init__(self, name, origPoint, width, height)
        Observable.__init__(self)

        self.navPath   = NavPath(self)
        self.physics   = Physics(0, rotFps, origPoint, trFps)
        self.moves     = []

        self.isSelected = False

    def log(self, msg):
        logEx(msg, category="Entity", name=self.name)

    def select(self):
        self.isSelected = True

    def unselect(self):
        self.isSelected = False

    def show(self):
        Entity.log(self, f"moves={len(self.moves)} navPath={self.navPath.isDone()}")
        Entity.log(self, f"square={self.square()} targetSquare={self.targetSquare()}")
        Entity.log(self, f"isMoving={self.isMoving()} isIdle={self.isIdle()}")
        self.physics.show()

    def addMove(self, move):
        self.moves.append(move)

    def clearMoves(self):
        self.moves.clear()

    def position(self):
        return self.physics.position()

    def targetPosition(self):
        return self.physics.targetPosition()

    def square(self):
        return self.physics.position().square()

    def targetSquare(self):
        p = self.physics.targetPosition()
        if p is None:
            return None
        else:
            return p.square()

    def isMoving(self):
        return self.physics.targetPosition() is not None

    def lookAt(self, hop):
        def lookAtHop():
            self.physics.lookAt(hop.point())
        self.addMove(lookAtHop)

    def moveTo(self, hop):
        def moveToHop():
            p = hop.point()
            if Compass.getSingleton().isObstacle(hop):
                Entity.log(self, f"moveToHop: Cannot move, obstacle at target hop {hop}")
            else:
                self.physics.moveTo(p)
                self.notifyObservers("entity-moved",
                                     oldSquare=self.square(), newSquare=hop)
        self.addMove(moveToHop)

    def isIdle(self):
        return self.physics.isDone() and len(self.moves) == 0

    def navigate(self, hops):
        assert len(hops) >= 1
        Entity.log(self, "navigate")
        self.clearMoves()
        self.navPath.set(hops)
        self.lookAt(self.navPath.hop)
        self.moveTo(self.navPath.hop)
        self.show()

    def nextHop(self):
        if self.navPath.isDone():
            return

        self.navPath.nextHop()
        if self.navPath.isDone():
            Entity.log(self, f"nextHop: Destination {self.square()} reached")
        else:
            nh = self.navPath.hop
            Entity.log(self, f"nextHop: Moving to hop {nh}")
            self.lookAt(nh)
            self.moveTo(nh)

    def nextMove(self):
        if not self.physics.isDone():
            return

        if len(self.moves) >= 1:
            move = self.moves.pop(0)
            move()
        else:
            self.nextHop()

    def update(self):
        self.physics.update()
        self.nextMove()
        Sprite.update(self)

    def drawSelection(self):
        if not self.isSelected:
            return
        p  = self.position().screen()
        bw = 1
        w  = self.width  + bw + bw
        h  = self.height + bw + bw
        pyxel.rectb(p.x - w // 2, p.y - h // 2, w, h, 8)

    def drawNavPath(self):
        if Config.mustLog("NavPath"):
            self.navPath.draw()

    def drawOverlay(self):
        if Config.mustLog("Physics"):
            p = self.position().screen()
            self.physics.drawAt(p.x, p.y)

    def draw(self):
        Sprite.draw(self)
