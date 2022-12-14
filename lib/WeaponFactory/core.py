import os.path
import pygame

from .arena      import Arena, Square, ArenaView, Camera, Region
from .const      import SCREEN_WIDTH, SCREEN_HEIGHT
from .input      import ModalInputHandler, Mouse
from .navigation import Compass, NavBeacon
from .resources  import Resources
from .utils      import Config, log_ex

COLOR_BLUE = (0, 0, 200)

EV_NAV = pygame.event.custom_type()

class Engine:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    def log(msg):
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

        flags = 0
        if config["screen"]["fullscreen"]:
            flags |= pygame.FULLSCREEN
            flags |= pygame.SCALED
        self.screen = pygame.display.set_mode(
            (config["screen"]["width"], config["screen"]["height"]), # size
            flags)                                                   # flags
        pygame.display.set_caption(config["caption"])
        pygame.mouse.set_visible(config["mouse"])

        self.entities          = []
        self.selected_entities = []
        self.debug_data        = None
        self.init_scene(arena_config)
        self.init_input()

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

        # Region
        def region_enable():
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
        drones = {
            "A": Square(10, 10),
            "B": Square(21, 10),
            "C": Square(10, 20),
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
        self.screen.fill(COLOR_BLUE)
        self._blit_scene(self.screen)
        self._blit_debug_data(self.screen)

    def _blit_scene(self, surface):
        av = ArenaView.singleton()
        av.blit(surface)
        if av.is_tactical:
            c        = Camera.singleton()
            entities = []
            a        = Arena.singleton()
            for v in range(c.v, c.v + c.height):
                for u in range(c.u, c.u + c.width):
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
