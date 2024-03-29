import pygame

from pygame            import Rect
from pytmx.util_pygame import load_pygame as tmx_load

if False:
    from .Drone          import Drone
from .Arena             import Arena
from .ArenaView         import ArenaView
from .Assets            import Assets
from .Camera            import Camera
from .Compass           import Compass
from .EngineClock       import EngineClock
from .EntityFactory     import EntityFactory
from .ModalInputHandler import ModalInputHandler
from .Mouse             import Mouse
from .NavBeacon         import NavBeacon
from .Region            import Region
from .Screen            import Screen
from .Square            import Square
from .colors            import COLOR_RED, COLOR_GREEN, COLOR_BLUE
from .debug             import DEBUG_REGION, DEBUG_TILE
from .utils             import log_ex

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

        pygame.init()
        Screen()

        Mouse.set_visible(False)
        Mouse.center()

        self.entities          = []
        self.selected_entities = []
        self.debug_data        = None
        self.init_arena()
        self.init_scene()
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

        # WIP
        def tactical_translate_to_mouse():
            Engine.log("tactical_translate_to_mouse")
            if len(self.entities) == 0:
                return
            self.entities[0]._physics.move_to( Mouse.world_point() )
        ih.addFunc("tactical_translate_to_mouse", tactical_translate_to_mouse)

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

        # Spawning entities
        a = Arena.singleton()
        self._spawn_locations = ["Mouse"]+ list(a.spawn_locations().keys())
        self._current_spawn_location = 0
        def spawn_location_next():
            self._current_spawn_location = (self._current_spawn_location + 1) \
                % len(self._spawn_locations)
        ih.addFunc("spawn_location_next", spawn_location_next)
        self._current_entity_type = 0
        self._entity_types = [
            "monolith-0",
            "monolith-1",
            "monolith-2",
            "monolith-3",
        ]
        def spawn_entity_type_next():
            self._current_entity_type = (self._current_entity_type + 1) \
                % len(self._entity_types)
        ih.addFunc("spawn_entity_type_next", spawn_entity_type_next)
        def spawn_entity():
            t = self._entity_types[self._current_entity_type]
            l = self._spawn_locations[self._current_spawn_location]
            if l == "Mouse":
                p = Mouse.world_point()
            else:
                p = Arena.singleton().spawn_location(l)
            Engine.log(f"Spawning entity at location '{l}'")
            e = EntityFactory.spawn(t, p)
            self.select(e)
            # monolith.register_observer(a)
            # monolith.notify_observers("entity-spawned", square=s)
            self.entities.append(e)
        ih.addFunc("spawn_entity", spawn_entity)

        ih.configure()

        self.input_handler = ih

    def clear_selection(self):
        for entity in self.selected_entities:
            entity.unselect()
        self.selected_entities = []

    def select(self, entity):
        entity.select()
        self.selected_entities.append(entity)

    def init_arena(self):
        a = Arena()
        Camera(a.surface_rect, a.square_size)
        # Compass(a.obstacles_matrix)

    def init_scene(self):
        # self.nav_beacon = NavBeacon()
        pass

    def update(self):
        self.input_handler.probe()
        self._update_scene()
        self._update_region()

    def _update_scene(self):
        ArenaView.singleton().update()

    def _update_region(self):
        Region.singleton().update_cursor()

    def _blit_region(self):
        Region.singleton().blit()

    def blit(self):
        Screen.singleton().reset()
        self._blit_scene()
        self._blit_region()

    def _blit_scene(self):
        c  = Camera.singleton()
        av = ArenaView.singleton()
        av.blit(c.rect)
        if av.is_tactical:
            self._blit_scene_tactical()
        else:
            self._blit_scene_strategic()
        self.input_handler.blit()

    def _blit_scene_strategic(self):
        pass

    def _blit_scene_tactical(self):
        a        = Arena.singleton()
        c        = Camera.singleton()
        (cx, cy) = c.rect.topleft
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
        if False:
            for e in entities:
                e.blit_debug()

    def _blit_debug(self):
        if DEBUG_TILE:
            self._blit_debug_square_at_mouse()
        self._blit_debug_mouse_coordinates()
        self._blit_debug_camera_coordinates()
        if DEBUG_REGION:
            self._blit_debug_region()
        self._blit_debug_square_properties()
        self._blit_debug_mouse_position()
        self._blit_debug_spawn_data()

    def _blit_debug_mouse_coordinates(self):
        a                 = Arena.singleton()
        mouse_position    = Mouse.world_point()
        mouse_square_rect = a.square_rect(mouse_position)
        text = " ".join([
            f"MOUSE:",
            f"screen: {Mouse.screen_point()}",
            f"world: {mouse_position}",
            f"square: {mouse_square_rect}",
        ])
        Screen.singleton().text(text, (0, 0))

    def _blit_debug_camera_coordinates(self):
        text = f"CAMERA: {Camera.singleton().rect}"
        Screen.singleton().text(text, (0, 10))

    def _blit_debug_region(self):
        text = "REGION: " + str(Region.singleton())
        Screen.singleton().text(text, (0, 20))

    def _blit_debug_square_properties(self):
        a = Arena.singleton()

        mouse_position = Mouse.world_point()
        mouse_square   = a.square(mouse_position)

        properties = a.get_square_properties(mouse_square)
        if properties is None:
            return
        text = []
        for k, v in properties.items():
            text.append(f"{k}: {v}")

        Screen.singleton().text(" ".join(text), (0, 30))

    def _blit_debug_square_at_mouse(self):
        a = Arena.singleton()

        # Build the mouse square in screen coordinates.
        mouse_position            = Mouse.world_point()
        mouse_square_rect         = a.square_rect(mouse_position)
        mouse_square_rect.topleft = Camera.singleton() \
                                          .screen_point(mouse_square_rect.topleft)

        # Show if the square is an obstacle or not.
        is_obstacle = a.is_obstacle(a.square(mouse_position))
        if is_obstacle:
            color = COLOR_RED
        else:
            color = COLOR_GREEN

        Screen.singleton().screen_draw_rect(color, mouse_square_rect, width=1)

    def _blit_debug_mouse_position(self):
        (mx, my) = Mouse.screen_point()
        Screen.singleton().screen_draw_rect(COLOR_BLUE, Rect((mx-1, my-1), (3, 3)))

    def _blit_debug_spawn_data(self):
        h = Camera.singleton().rect.height - 10
        l = self._spawn_locations[self._current_spawn_location]
        t = self._entity_types[self._current_entity_type]
        Screen.singleton().text(f"SPAWN: Location: {l} Type: {t}", (0, h))

    def run(self):
        self.is_running = True
        while self.is_running:
            self.update()
            self.blit()
            EngineClock.singleton().tick()
            self._blit_debug()
            pygame.display.flip()
