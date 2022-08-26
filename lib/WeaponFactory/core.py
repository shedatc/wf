import os.path
import pyxel

from os import chdir, getcwd

from .arena      import Arena, Square, ArenaView, Camera, Region
from .const      import SCREEN_WIDTH, SCREEN_HEIGHT
from .input      import ModalInputHandler, Mouse
from .navigation import Compass, NavBeacon
from .resources  import Resources
from .utils      import Config, logEx

class Engine:

    singleton = None

    def getFrameRate():
        assert Engine.singleton is not None
        self = Engine.singleton

        return self.fps

    def log(msg):
        logEx(msg, category="Engine", frame=False)

    def __init__(self, profiling=False):
        assert Engine.singleton is None
        Engine.singleton = self

        Engine.log(f"Working Directory: {getcwd()}")
        Engine.log(f"Profiling: {profiling}")
        if profiling:
            import cProfile
            self.profile = cProfile.Profile()
            self.profile.enable()
        else:
            self.profile = None

        config = Config.load("engine.json")
        self.fps = config["fps"]

        arenaConfig = config["arena"]
        arenaName   = arenaConfig["name"]

        self.resources = Resources()

        orig_cwd = getcwd()
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT,
                   title=config["caption"], fps=self.fps,
                   quit_key=pyxel.KEY_NONE)
        chdir(orig_cwd)
        pyxel.mouse(config["mouse"])

        pyxel.load( self.resources.locateResource("pyxel-resource", f"{arenaName}.pyxres") )

        self.entities         = []
        self.selectedEntities = []
        self.initScene(arenaConfig)

        self.debugData = None

        self.initInput()

        Engine.log("Ready")

    def initInput(self):
        ih = ModalInputHandler()

        def wfQuit():
            if self.profile is not None:
                from io     import StringIO
                from pstats import SortKey, Stats

                self.profile.disable()
                s  = StringIO()
                ps = Stats(self.profile, stream=s).sort_stats(SortKey.CUMULATIVE)
                ps.print_stats()
                with open("wf.pstats", "w") as f:
                    f.write(s.getvalue())
            pyxel.quit()
        ih.addFunc("quit", wfQuit)

        # DEBUG
        def debugTileDataFromMouse():
            self.debugData = Arena.getSingleton().tileDataFromMouse()
        ih.addFunc("debugTileDataFromMouse", debugTileDataFromMouse)

        # DEBUG
        def debugSquareCoordinatesFromMouse():
            self.debugData = Square(0, 0).fromMouse()
        ih.addFunc("debugSquareCoordinatesFromMouse", debugSquareCoordinatesFromMouse)

        # Moving the camera
        def cameraUp():
            Camera.getSingleton().up()
        ih.addFunc("cameraUp", cameraUp)
        def cameraDown():
            Camera.getSingleton().down()
        ih.addFunc("cameraDown", cameraDown)
        def cameraLeft():
            Camera.getSingleton().left()
        ih.addFunc("cameraLeft", cameraLeft)
        def cameraRight():
            Camera.getSingleton().right()
        ih.addFunc("cameraRight", cameraRight)
        def cameraToMouse():
            (mx, my) = Mouse.getCoords()
            Camera.getSingleton().centeredMove(mx, my)
        ih.addFunc("cameraToMouse", cameraToMouse)

        def arenaViewToggle():
            if ArenaView.getSingleton().toggle().isTactical:
                ih.enterMode("tactical/select")
            else:
                ih.enterMode("strategic/select")
        ih.addFunc("arenaViewToggle", arenaViewToggle)

        def tacticalMoveToMouse():
            self.navBeacon.fromMouse()
            if self.navBeacon.isEnabled:
                for entity in self.selectedEntities:
                    Compass.getSingleton().navigate(entity, self.navBeacon.square)
        ih.addFunc("tacticalMoveToMouse", tacticalMoveToMouse)
        def strategicMoveToMouse():
            (mx, my) = Mouse.getCoords()
            if self.navBeacon.tryMove( Square(mx, my) ):
                for entity in self.selectedEntities:
                    Compass.getSingleton().navigate(entity, self.navBeacon.square)
        ih.addFunc("strategicMoveToMouse", strategicMoveToMouse)

        # Region
        def regionEnable():
            self.clearSelection()
            Region.getSingleton().enable()
        ih.addFunc("regionEnable", regionEnable)
        def regionDisable():
            entities = Region.getSingleton().disable()
            if entities is None:
                self.clearSelection()
            else:
                for entity in entities:
                    self.select(entity)
        ih.addFunc("regionDisable", regionDisable)

        ih.configure()

        self.inputHandler = ih

    def clearSelection(self):
        for entity in self.selectedEntities:
            entity.unselect()
        self.selectedEntities = []

    def select(self, entity):
        entity.select()
        self.selectedEntities.append(entity)

    def initScene(self, arenaConfig):
        a = Arena(arenaConfig)
        Compass(a.obstaclesMatrix)

        # Spawn some drones
        drones = {
            "A": Square(20, 10),
            "B": Square(21, 10),
            "C": Square(10, 30),
        }
        for name, square in drones.items():
            drone = Drone(square)
            drone.name = name
            drone.registerObserver(a)
            drone.notifyObservers("entity-spawned", square=drone.position().square())
            self.entities.append(drone)

        self.navBeacon = NavBeacon()

    def update(self):
        self.inputHandler.probe()
        self.updateScene()

    def updateScene(self):
        ArenaView.getSingleton().update()
        for entity in self.entities:
            entity.update()

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.drawScene()
        self.drawDebugData()

    def drawScene(self):
        av = ArenaView.getSingleton()
        av.draw()
        if av.isTactical:
            c        = Camera.getSingleton()
            entities = []
            a        = Arena.getSingleton()
            for v in range(c.v, c.v + c.height):
                for u in range(c.u, c.u + c.width):
                    entities.extend( a.entitiesAtSquare(u, v) )
            for e in entities:
                e.drawNavPath()
            for e in entities:
                e.drawSelection()
            for e in entities:
                e.draw()
            for e in entities:
                e.drawOverlay()
        self.inputHandler.draw()

    def drawDebugData(self):
        if self.debugData is not None:
            pyxel.text(0, 0, f"{self.debugData}", pyxel.COLOR_BLACK)

    def run(self):
        pyxel.run(self.update, self.draw)

class AnimationSandbox(Engine):

    def __init__(self, configDir="etc/animation"):
        Engine.__init__(self, configDir=configDir)

    def pickSprite(self, sprite):
        self.sprite            = sprite
        self.animations        = list( sprite.animation.animations.values() )
        self.animationsCount   = len(self.animations)
        self.setAnimationByIndex(0)

    def initScene(self):
        self.pickSprite( Drone(Square(15, 15)) )

    def updateScene(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.previousAnimation()
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.nextAnimation()
        elif pyxel.btnp(pyxel.KEY_SPACE):
            self.sprite.animation.toggle()
        elif pyxel.btnp(pyxel.KEY_RIGHT) and self.sprite.animation.current.isPaused:
            self.nextFrame()
        self.sprite.update()

    def nextFrame(self):
        animation = self.sprite.animation.current
        animation.resume()
        animation.nextFrame()
        animation.pause()

    def setAnimationByIndex(self, index):
        assert index >= 0
        assert index < self.animationsCount
        self.currentAnimationIndex = index
        self.currentAnimationName  = self.animations[index].name
        self.sprite.animation.pause()
        self.sprite.animation.select( self.currentAnimationName )
        self.sprite.animation.pause()
        Engine.log(f"Animation: {self.currentAnimationIndex}<{self.currentAnimationName}>")

    def nextAnimation(self):
        i = self.currentAnimationIndex + 1
        if i == len(self.animations):
            i = 0
        self.setAnimationByIndex(i)

    def previousAnimation(self):
        i = self.currentAnimationIndex - 1
        if i < 0:
            i = len(self.animations) - 1
        self.setAnimationByIndex(i)

    def drawScene(self):
        # List available animations
        y = ( pyxel.height - self.animationsCount * 10 ) / 2
        for a in range(self.animationsCount):
            animation = self.animations[a]
            if a == self.currentAnimationIndex:
                pyxel.text(0, y, f"{animation.name}", pyxel.COLOR_WHITE)
            else:
                pyxel.text(0, y, f"{animation.name}", pyxel.COLOR_NAVY)
            y += 10

        # Frames Data
        x = pyxel.width - 60
        y = ( pyxel.height - 2 * 10 ) / 2
        animation = self.sprite.animation.current
        pyxel.text(x, y,      f"Current: {animation.current}", pyxel.COLOR_WHITE)
        pyxel.text(x, y + 10, f"Last:    {animation.last}", pyxel.COLOR_WHITE)

        # Draw the animatede sprite
        self.sprite.draw()

from .drone import Drone
