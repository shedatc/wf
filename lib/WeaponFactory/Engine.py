import pygame

from pygame            import Rect
from pytmx.util_pygame import load_pygame as tmx_load

from .AnimationClock import AnimationClock
if False:
    from .Drone          import Drone
from .Arena             import Arena
from .ArenaView         import ArenaView
from .Camera            import Camera
from .ModalInputHandler import ModalInputHandler
from .Monolith          import Monolith
from .Mouse             import Mouse
from .Region            import Region
from .Screen            import Screen
from .Square            import Square

from .assets            import Assets
from .const             import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_BLACK
from .navigation        import Compass, NavBeacon
from .utils             import Config, log_ex, sz

EV_NAV = pygame.event.custom_type()

class Engine:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, profiling=False):
        assert Engine._singleton is None
        Engine._singleton = self

        # FIXME Log things like SDL version, etc…

        Engine.log(f"Profiling: {profiling}")
        if profiling:
            import cProfile
            self.profile = cProfile.Profile()
            self.profile.enable()
        else:
            self.profile = None

        config       = Config.singleton().load("engine.json")
        arena_config = config["arena"] # FIXME Should be in some arena.json

        pygame.init()
        Screen((config["screen"]["width"], config["screen"]["height"]),
               caption=config["caption"])

        Mouse.set_visible(config["mouse"])
        Mouse.center()

        self.entities          = []
        self.selected_entities = []
        self.debug_data        = None
        self.init_arena(arena_config)
        self.init_scene()
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
            # Center the camera on mouse position
            c                             = Camera.singleton()
            (square_width, square_height) = Arena.singleton().square_size
            (cu, cv)                      = c.uv()
            (mx, my)                      = Mouse.screen_point()
            (mu, mv)                      = (mx // square_width, my // square_height)
            c.centered_move(mu + cu, mv + cv)

            Mouse.center()
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
            (mx, my) = Mouse.screen_point()
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

    def init_arena(self, arena_config):
        a = Arena(arena_config)
        Camera(a.surface_rect, a.square_size)
        # Compass(a.obstacles_matrix)

    def init_scene(self):
        self._spawn_monolith()
        # self._spawn_drones()
        # self.nav_beacon = NavBeacon()

    def _spawn_monolith(self):
        if False:
            # Use mouse position
            (cx, cy)          = Camera.singleton().rect.topleft
            (mx, my)          = Mouse.screen_point()
            monolith_position = (mx + cx, my + cy)
        else:
            monolith_position = (290, 130)
        monolith          = Monolith(monolith_position)
        # monolith.register_observer(a)
        # monolith.notify_observers("entity-spawned", square=s)
        self.entities.append(monolith)

    # Spawn some drones
    def _spawn_drones(self):
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

    def update(self):
        self.input_handler.probe()
        self.update_scene()

    def update_scene(self):
        ArenaView.singleton().update()

        if False:
            (mouse_position)          = Mouse.screen_point()
            self.entities[0].position = mouse_position
            Engine.log(f"Mouse position: {mouse_position}")

        for entity in self.entities:
            entity.update()

    def blit(self):
        Screen.singleton().reset()
        self._blit_scene()
        self._blit_debug_data()

    def _blit_scene(self):
        c  = Camera.singleton()
        av = ArenaView.singleton()
        av.blit(c.rect)

        (cx, cy) = c.rect.topleft

        if av.is_tactical:
            a        = Arena.singleton()
            entities = []
            if True:
                entities = self.entities
            else:
                for v in range(c.v, c.v + c.height - 1):
                    for u in range(c.u, c.u + c.width - 1):
                        entities.extend( a.entities_at_square(u, v) )

            # Engine.log(f"len(entities)={len(entities)}")
            if False:
                for e in entities:
                    e.blit_nav_path(surface)
            if False:
                for e in entities:
                    e.blit_selection(surface)
            for e in entities:
                (x, y)          = e.position
                screen_position = (x - cx, y - cy)
                e.blit_at(screen_position)
            if False:
                for e in entities:
                    e.blit_overlay(surface)
        self.input_handler.blit()

    def _blit_debug_data(self):
        self._blit_debug_square_at_mouse()
        # self._blit_debug_misc()
        self._blit_debug_mouse_position()

    def _blit_debug_square_at_mouse(self):
        a = Arena.singleton()

        # Build the mouse square in screen coordinates.
        mouse_position       = Mouse.world_point()
        mouse_square         = a.square_rect(mouse_position)
        mouse_square.topleft = Camera.singleton().screen_point(mouse_square.topleft)


        is_obstacle = a.is_obstacle(a.square(mouse_position))
        if is_obstacle:
            color = COLOR_RED
        else:
            color = COLOR_GREEN

        Screen.singleton().draw_rect(color, mouse_square, width=1)

    def _blit_debug_mouse_position(self):
        (mx, my) = Mouse.screen_point()
        Screen.singleton().draw_rect(COLOR_BLUE, Rect((mx-1, my-1), (3, 3)))

    def _blit_debug_misc(self, surface):
        a                             = Arena.singleton()
        (mx, my)                      = Mouse.screen_point()
        m                             = Point(mx, my)
        c                             = Camera.singleton()
        (square_width, square_height) = a.square_size
        mouse_square                  = Square(mx // square_width  + c.u,
                                               my // square_height + c.v)
        (mu, mv)                      = (mouse_square.u, mouse_square.v)

        # Describe square at mouse
        tm          = a.tm
        is_obstacle = a.is_obstacle(mouse_square)
        if mouse_square.u == 0 and mouse_square.v == 0:
            Engine.log(f"is_obstacle={is_obstacle}")

        # Tile and is_obstacle
        pixels = Rect((mx - square_width // 2, my - square_height // 2),
                      (square_width,           square_height))
        if is_obstacle:
            color = COLOR_RED
        else:
            color = COLOR_GREEN
        pygame.draw.rect(surface, color, pixels, width=1)

        # Mouse Pointer
        pygame.draw.rect(surface, COLOR_BLUE, Rect(m.xy(), (1, 1)))

        # Display various coordinates
        (cx, cy) = c.xy()
        (cu, cv) = c.uv()
        font      = pygame.font.Font(None, 15)
        text = [f"Mouse: {m} {mouse_square}",
                f"Camera: ({cx}, {cy}) [{cu}, {cv}]"]
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
        self.is_running = True
        while self.is_running:
            self.update()
            self.blit()
            pygame.display.flip()
            AnimationClock.singleton().tick()
