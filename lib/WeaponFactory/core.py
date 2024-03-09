import os.path
import pygame

from pygame            import Rect
from pytmx.util_pygame import load_pygame as tmx_load

from .arena      import Arena, Point, Square, ArenaView, Camera, Region
from .const      import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_BLACK
from .const      import SCREEN_WIDTH, SCREEN_HEIGHT, SQUARE_SIZE, TILE_WIDTH, TILE_HEIGHT
from .const      import ISO_TILE_WIDTH, ISO_TILE_HEIGHT
from .input      import ModalInputHandler, Mouse
from .navigation import Compass, NavBeacon
from .resources  import Resources
from .utils      import Config, log_ex, sz

EV_NAV = pygame.event.custom_type()

class Engine:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category="Engine")

    def __init__(self, profiling=False):
        assert Engine._singleton is None
        Engine._singleton = self

        Engine.log(f"Profiling: {profiling}")
        if profiling:
            import cProfile
            self.profile = cProfile.Profile()
            self.profile.enable()
        else:
            self.profile = None

        config         = Config.singleton().load("engine.json")
        self.fps       = config["fps"]
        arena_config   = config["arena"]
        arena_name     = arena_config["name"]
        self.resources = Resources()

        pygame.init()
        wanted_screen_size = (config["screen"]["width"], config["screen"]["height"])
        self.screen = pygame.display.set_mode(wanted_screen_size,
                                              pygame.FULLSCREEN | pygame.SCALED)
        Engine.log(f"screen: wanted={sz(wanted_screen_size)}"
                   + f" current={sz(self.screen.get_size())}")

        pygame.display.set_caption(config["caption"])
        pygame.mouse.set_visible(config["mouse"])

        self.entities          = []
        self.selected_entities = []
        self.debug_data        = None
        self.init_scene(arena_config)
        self.init_input()

        self._misc_tm = tmx_load( Resources.locate("tilemap", "misc.tmx") )

        Engine.log("Ready")

    def quit(self):
        if self.profile is not None:
            from io     import StringIO
            from pstats import SortKey, Stats

            self.profile.disable()
            s  = StringIO()
            ps = Stats(self.profile, stream=s).sort_stats(SortKey.CUMULATIVE)
            ps.print_stats()
            with open("wf.pstats", "w") as f:
                f.write(s.getvalue())
        self.is_running = False

    def init_input(self):
        ih = ModalInputHandler()

        ih.addFunc("quit", lambda: self.quit())

        # DEBUG
        def debug_tile_data_from_mouse():
            self.debug_data = Arena.singleton().tile_data_from_mouse()
        ih.addFunc("debug_tile_data_from_mouse", debug_tile_data_from_mouse)

        # DEBUG
        def debug_square_coordinates_from_mouse():
            self.debug_data = Square(0, 0).from_mouse()
        ih.addFunc("debug_square_coordinates_from_mouse", debug_square_coordinates_from_mouse)

        # Moving the camera
        def camera_up():
            Camera.singleton().up()
        ih.addFunc("camera_up", camera_up)
        def camera_down():
            Camera.singleton().down()
        ih.addFunc("camera_down", camera_down)
        def camera_left():
            Camera.singleton().left()
        ih.addFunc("camera_left", camera_left)
        def camera_right():
            Camera.singleton().right()
        ih.addFunc("camera_right", camera_right)
        def camera_to_mouse():
            (mx, my) = Mouse.get_coords()
            Camera.singleton().centered_move(mx, my)
        ih.addFunc("camera_to_mouse", camera_to_mouse)

        def arena_view_toggle():
            if ArenaView.singleton().toggle().is_tactical:
                ih.enterMode("tactical/select")
            else:
                ih.enterMode("strategic/select")
        ih.addFunc("arena_view_toggle", arena_view_toggle)

        def tactical_move_to_mouse():
            self.nav_beacon.from_mouse()
            if self.nav_beacon.is_enabled:
                for entity in self.selected_entities:
                    Compass.singleton() \
                           .navigate(entity, self.nav_beacon.square)
        ih.addFunc("tactical_move_to_mouse", tactical_move_to_mouse)

        def strategic_move_to_mouse():
            (mx, my) = Mouse.get_coords()
            if self.nav_beacon.try_move( Square(mx, my) ):
                for entity in self.selected_entities:
                    path_found = Compass.singleton() \
                                        .navigate(entity, self.nav_beacon.square)
        ih.addFunc("strategic_move_to_mouse", strategic_move_to_mouse)

        def describe_square(square):
            tm    = Arena.singleton().tm
            level = tm.lookup_tile_property(square, "level")
            if level is None:
                Engine.log(f"Tile at {square} has no level")
            else:
                Engine.log(f"Tile at {square} is at level {level}")

            is_obstacle = tm.lookup_tile_property(square, "is_obstacle")
            if is_obstacle in [None, False]:
                Engine.log(f"Tile is not an obstacle")
            else:
                Engine.log(f"Tile is an obstacle")

        # Region
        def region_enable():

            # Describe the square at mouse.
            c        = Camera.singleton()
            (mx, my) = Mouse.get_coords()
            mouse_square = Square(mx // TILE_WIDTH  + c.u,
                                  my // TILE_HEIGHT + c.v)
            Engine.log(f"mouse: xy=({mx}, {my}) square={mouse_square}")
            describe_square(mouse_square)

            self.clear_selection()
            Region.singleton().enable()
        ih.addFunc("region_enable", region_enable)
        def region_disable():
            entities = Region.singleton().disable()
            if entities is None:
                self.clear_selection()
            else:
                for entity in entities:
                    self.select(entity)
        ih.addFunc("region_disable", region_disable)

        ih.configure()

        self.input_handler = ih

    def clear_selection(self):
        for entity in self.selected_entities:
            entity.unselect()
        self.selected_entities = []

    def select(self, entity):
        entity.select()
        self.selected_entities.append(entity)

    def init_scene(self, arena_config):
        a = Arena(arena_config)
        Compass(a.obstacles_matrix)

        # Spawn some drones
        if False:
            drones = {
                "A": Square(5,  10),
                "B": Square(11, 10),
                "C": Square(5,  20),
            }
            for name, square in drones.items():
                drone      = Drone(square)
                drone.name = name
                drone.register_observer(a)
                drone.notify_observers("entity-spawned", square=drone.position().square())
                self.entities.append(drone)

        self.nav_beacon = NavBeacon()

    def update(self):
        self.input_handler.probe()
        self.update_scene()

    def update_scene(self):
        ArenaView.singleton().update()
        for entity in self.entities:
            entity.update()

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        self._blit_scene(self.screen)
        self._blit_debug_data(self.screen)

    def _blit_scene(self, surface):
        av = ArenaView.singleton()
        av.blit(surface)
        if av.is_tactical:
            c        = Camera.singleton()
            entities = []
            a        = Arena.singleton()
            for v in range(c.v, c.v + c.height - 1):
                for u in range(c.u, c.u + c.width - 1):
                    entities.extend( a.entities_at_square(u, v) )
            for e in entities:
                e.blit_nav_path(surface)
            for e in entities:
                e.blit_selection(surface)
            for e in entities:
                e.blit(surface)
            for e in entities:
                e.blit_overlay(surface)
        self.input_handler.blit(surface)

    def _blit_debug_data(self, surface):
        (mx, my) = Mouse.get_coords()
        m        = Point(mx, my)

        if False:
            o = m.copy().to_ortho().to_square()
            pygame.draw.rect(surface,
                             COLOR_GREEN,
                             Rect(o.pos(),
                                  (SQUARE_SIZE, SQUARE_SIZE)),
                             width=1)

        if True:
            t   = m.copy().to_tile()
            img = self._misc_tm.get_tile_image(0, 0, 0)
            surface.blit(img, t.pos())

        i = m.copy()
        pygame.draw.rect(surface, COLOR_RED, Rect(i.pos(), (2, 2)))

        if self.debug_data is None:
            return

        # FIXME
        # pyxel.text(0, 0, f"{self.debug_data}", pyxel.COLOR_BLACK)
        raise NotImplementedError("Must replace pyxel.text")

    def run(self):
        clock            = pygame.time.Clock()
        self.is_running  = True
        self.frame_count = 0
        while self.is_running:
            self.update()
            self.draw()
            pygame.display.flip()
            self.frame_count += 1
            clock.tick(self.fps)

from .drone import Drone
