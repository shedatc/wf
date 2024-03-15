import pygame

from .Square     import Square
from .assets     import Assets
from .const      import OBSTACLE, WALKABLE
from .navigation import Compass
from .tilemap    import Tilemap
from .utils      import Config, log_ex, sz

# An arena is the terrain with all its obstacles.
class Arena:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def log_entities_matrix(self):
        if not Config.singleton().must_log("Arena"):
            return
        Arena.log(f"Entities Matrix {self.width}x{self.height}:")
        for v in range(self.height):
            for u in range(self.width):
                    entities = self.entities_matrix[v][u]
                    if len(entities) >= 1:
                        msg = f"[{u}, {v}]"
                        for entity in entities:
                            msg += f" {entity.name}"
                        Arena.log(msg)

    def log_obstacles_matrix(self):
        if not Config.singleton().must_log("Arena"):
            return
        Arena.log(f"Obstacles Matrix:")
        for v in range(self.height):
            msg = ''
            for u in range(self.width):
                    if self.obstacles_matrix[v][u] == OBSTACLE:
                        msg += 'x'
                    else:
                        msg += ' '
            Arena.log(msg)

    def __init__(self, config):
        assert Arena._singleton is None
        Arena._singleton = self

        self.name = config["name"]

        # Tilemap
        self.tm                   = Tilemap(self.name)
        (self.width, self.height) = self.tm.map_size
        self.square_size          = (self.tm.tile_size)

        Arena.log(f"Name:        {self.name}")
        Arena.log(f"Size:        {sz((self.width, self.height))}")
        Arena.log(f"Square Size: {sz(self.square_size)}")

        # Resize the screen if the tilemap is smaller
        (screen_width, screen_height) = pygame.display.get_surface().get_size()
        (tm_width, tm_height)         = self.tm.surface_size
        if tm_width < screen_width or tm_height < screen_height:
            new_screen_width  = min(screen_width, tm_width)
            new_screen_height = min(screen_height, tm_height)
            Arena.log(f"Resizing screen: {screen_width}x{screen_height} → {new_screen_width}x{new_screen_height}")
            self.screen = pygame.display.set_mode((new_screen_width, new_screen_height),
                                                  pygame.FULLSCREEN | pygame.SCALED)

        # Strategic View
        if False:
            sv_path               = Assets.locate("image", f"{self.name}-sv.png")
            self.sv               = pygame.image.load(sv_path)
            (sv_width, sv_height) = self.sv.get_size()
            Arena.log(f"sv: path={sv_path} size={sv_width}x{sv_height}")
            assert sv_width  == self.width,  "SV image width must match tilemap width"
            assert sv_height == self.height, "SV image height must match tilemap height"

        # Obstacles:
        self.obstacles_matrix = [[WALKABLE] * self.width for i in range(self.height)]
        for v in range(self.height):
            for u in range(self.width):
                if self.tm.is_obstacle(u, v):
                    self.obstacles_matrix[v][u] = OBSTACLE
        # self.log_obstacles_matrix()

        # Entities:
        self.entities_matrix = [[1] * self.width for i in range(self.height)]
        for v in range(self.height):
            for u in range(self.width):
                self.entities_matrix[v][u] = []
        self.log_entities_matrix()

    def size(self):
        return (self.width, self.height)

    def tile_data_from_mouse(self):
        return Square(0, 0).from_mouse().tile_data()

    def is_obstacle(self, square):
        return self.obstacles_matrix[square.v][square.u] == OBSTACLE

    def entities_at_square(self, u, v):
        try:
            return self.entities_matrix[v][u]
        except IndexError:
            return []

    def notify(self, event, observable, **kwargs):
        if event == "entity-spawned":
            self.entity_spawned(observable, kwargs["square"])
        elif event == "entity-moved":
            self.entity_moved(observable, kwargs["old_square"], kwargs["new_square"])
        else:
            raise AssertionError(f"Event not supported: {event}")

    def entity_spawned(self, entity, square):
        Arena.log(f"Entity {entity.name} spawned on {square}")

        (u, v) = (square.u, square.v)
        self.entities_matrix[v][u].append(entity)
        self.obstacles_matrix[v][u] = OBSTACLE
        Compass.singleton().set_obstacle(square)
        Arena.log(f"Obstacle at square {square}")
        self.log_entities_matrix()

    def entity_moved(self, entity, old_square, new_square):
        Arena.log(f"Entity {entity.name} moved from {old_square} to {new_square}")

        (ou, ov) = (old_square.u, old_square.v)
        self.entities_matrix[ov][ou].remove(entity)
        if (len(self.entities_matrix[ov][ou]) == 0):
            self.obstacles_matrix[ov][ou] = WALKABLE
            Compass.singleton().set_walkable(old_square)
            Arena.log(f"No more obstacle at square {old_square}")

        (nu, nv) = (new_square.u, new_square.v)
        self.entities_matrix[nv][nu].append(entity)
        assert len(self.entities_matrix[nv][nu]) == 1, "Stacking not allowed for now"

        self.obstacles_matrix[nv][nu] = OBSTACLE
        Compass.singleton().set_obstacle(new_square)
        Arena.log(f"Obstacle at square {new_square}")
        self.log_entities_matrix()
