import os.path
import pygame

from pygame            import Rect
from pytmx.util_pygame import load_pygame as tmx_load

from .arena      import Arena, Point, Square, ArenaView, Camera, Region
from .const      import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_BLACK, COLOR_WHITE
from .input      import ModalInputHandler, Mouse
from .navigation import Compass, NavBeacon
from .assets     import Assets
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

        pygame.init()
        wanted_screen_size = (config["screen"]["width"], config["screen"]["height"])
        self.screen = pygame.display.set_mode(wanted_screen_size,
                                              pygame.FULLSCREEN | pygame.SCALED)

        Engine.log(f"Screen: {sz(self.screen.get_size())} ({sz(wanted_screen_size)})")
        Engine.log(f"FPS:    {self.fps}")

        pygame.display.set_caption(config["caption"])
        pygame.mouse.set_visible(config["mouse"])

        self.entities          = []
        self.selected_entities = []
        self.debug_data        = None
        self.init_scene(arena_config)
        self.init_input()

        self._debug_tm = tmx_load( Assets.locate("tilemap", "debug.tmx") )

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
            (mx, my) = Mouse.pos()
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
            (mx, my) = Mouse.pos()
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
        if True: # XXX
            return
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
        (mx, my)     = Mouse.pos()
        m            = Point(mx, my)
        c            = Camera.singleton()
        (tile_width, tile_height) = Arena.singleton().tm.tile_size
        mouse_square = Square(mx // tile_width  + c.u,
                              my // tile_height + c.v)
        (mu, mv)     = (mouse_square.u, mouse_square.v)

        # Describe square at mouse
        tm          = Arena.singleton().tm
        is_obstacle = mouse_square.is_obstacle()
        if mouse_square.u == 0 and mouse_square.v == 0:
            Engine.log(f"is_obstacle={is_obstacle}")

        # Tile and is_obstacle
        o      = mouse_square.point().screen()
        pixels = Rect((o.x - tile_width // 2, o.y - tile_height // 2),
                      (tile_width,            tile_height))
        if is_obstacle:
            color = COLOR_RED
        else:
            color = COLOR_GREEN
        pygame.draw.rect(surface, color, pixels, width=1)

        # Mouse Pointer
        pygame.draw.rect(surface, COLOR_BLUE, Rect(m.pos(), (1, 1)))

        # Display various coordinates
        font      = pygame.font.Font(None, 15)
        text = [f"Mouse: {m} {mouse_square}",
                f"Camera: {c.pos()}"]
        text_surf = font.render(" ".join(text),  # text
                                True,            # antialias
                                COLOR_GREEN,     # color
                                COLOR_BLACK)     # background
        surface.blit(text_surf, (0, 0))

        # Tile Properties:
        tile_properties = tm.get_tile_properties(mu, mv)
        if tile_properties is not None:
            text = []
            for k, v in tile_properties.items():
                text.append(f"{k}: {v}")
            text_surf = font.render(" ".join(text),  # text
                                    True,            # antialias
                                    COLOR_GREEN,     # color
                                    COLOR_BLACK)     # background
            surface.blit(text_surf, (0, 10))


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
