import pygame

from pygame import Rect

from .Assets  import Assets
from .Compass import Compass
from .Config  import Config
from .Tilemap import Tilemap
from .utils   import log_ex, sz

OBSTACLE = 0
WALKABLE = 1

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
        Arena.log(f"Entities Matrix {self.rect.width}x{self.rect.height}:")
        for v in range(self.rect.height):
            for u in range(self.rect.width):
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
        for v in range(self.rect.height):
            msg = ''
            for u in range(self.rect.width):
                    if self.obstacles_matrix[v][u] == OBSTACLE:
                        msg += 'x'
                    else:
                        msg += ' '
            Arena.log(msg)

    def blit(self, source_rect):
        self._tm.blit(source_rect)

    def __init__(self):
        assert Arena._singleton is None
        Arena._singleton = self

        config    = Config.singleton().load("arena.json")
        self.name = config["name"]

        # Tilemap
        self._tm          = Tilemap(self.name)
        self.square_size  = self._tm.tile_rect.size          # pixels
        self.rect         = Rect((0, 0), self._tm.rect.size) # squares
        self.surface_rect = self._tm.surface_rect            # pixels

        self._spawn_locations = {}
        if "Spawn Location" in self._tm.locations:
            self._fetch_spawn_locations(self._tm.locations["Spawn Location"])

        Arena.log(f"Arena '{self.name}':")
        Arena.log(f"    Rectangle:    {sz(self.rect.size)} squares")
        Arena.log(f"    Square Size:  {sz(self.square_size)} pixels")
        Arena.log(f"    Surface Size: {sz(self.surface_rect.size)} pixels")

        # Resize the screen if the tilemap is smaller
        (screen_width, screen_height) = pygame.display.get_surface().get_size() # pixels
        (tm_width, tm_height)         = self.surface_rect.size                  # pixels
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
        self.obstacles_matrix = [[WALKABLE] * self.rect.width for _ in range(self.rect.height)]
        for y in range(self.rect.height):
            for x in range(self.rect.width):
                if self._tm.is_obstacle(x, y):
                    self.obstacles_matrix[y][x] = OBSTACLE
        # self.log_obstacles_matrix()

        # Entities:
        self.entities_matrix = [[1] * self.rect.width for _ in range(self.rect.height)]
        for y in range(self.rect.height):
            for x in range(self.rect.width):
                self.entities_matrix[y][x] = []
        self.log_entities_matrix()

    def is_obstacle(self, square):
        (x, y) = square
        return self.obstacles_matrix[y][x] == OBSTACLE

    # Return the point in world coordinates corresponding to the center of the
    # given square.
    def point(self, square):
        (x, y)                        = square
        (square_width, square_height) = self.square_size
        return (x * square_width  + square_width  // 2,
                y * square_height + square_height // 2)

    # Return the square to which the point belong.
    def square(self, world_point):
        (x, y)   = world_point
        (w, h)   = self.square_size
        (sx, sy) = (int(x // w), int(y // h))
        return (sx, sy)

    # Return the rectangle corresponding to the square to which the point
    # belong. The point must be in world coordinates. The returned rectangle is
    # also in world coordinates.
    def square_rect(self, world_point):
        (x, y) = self.square(world_point)
        (w, h) = self.square_size
        return Rect((x * w, y * h),
                    self.square_size)

    # Return the rectangle in squares, correponding to the given rectangle in
    # world coordinates.
    def world_squares(self, world_rect):
        assert world_rect.width > 0
        assert world_rect.height > 0
        topleft                       = self.square(world_rect.topleft)
        (square_width, square_height) = self.square_size
        w                             = 1 + world_rect.width  // square_width
        h                             = 1 + world_rect.height  // square_height
        return Rect(topleft, (w, h))

    def entities(self, world_rect):
        rect     = self.world_squares(world_rect)
        entities = []
        for y in range(rect.y, rect.y + rect.height):
            for x in range(rect.x, rect.x + rect.width):
                assert type(self.entities_matrix[y][x]) is list
                entities += self.entities_matrix[y][x]
        Arena.log(f"Rect:     {world_rect} → {rect}")
        Arena.log(f"Entities: {entities}")
        return entities

    def notify(self, event, observable, **kwargs):
        if event == "entity-spawned":
            self.entity_spawned(observable, kwargs["square"])
        elif event == "entity-moved":
            self.entity_moved(observable, kwargs["old_square"], kwargs["new_square"])
        else:
            raise AssertionError(f"Event not supported: {event}")

    def entity_spawned(self, entity, square):
        Arena.log(f"Entity {entity.name} spawned at {square}")

        (x, y) = square
        self.entities_matrix[y][x].append(entity)
        self.obstacles_matrix[y][x] = OBSTACLE
        if False:
            Compass.singleton().set_obstacle(square)
        Arena.log(f"Obstacle at square {square}")
        self.log_entities_matrix()

    def entity_moved(self, entity, old_square, new_square):
        Arena.log(f"Entity {entity.name} moved from {old_square} to {new_square}")

        (ox, oy) = old_square
        self.entities_matrix[oy][ox].remove(entity)
        if (len(self.entities_matrix[oy][ox]) == 0):
            self.obstacles_matrix[oy][ox] = WALKABLE
            if False:
                Compass.singleton().set_walkable(old_square)
            Arena.log(f"No more obstacle at square {old_square}")

        (nx, ny) = new_square
        self.entities_matrix[ny][nx].append(entity)
        assert len(self.entities_matrix[ny][nx]) == 1, "Stacking not allowed for now"

        self.obstacles_matrix[ny][nx] = OBSTACLE
        if False:
            Compass.singleton().set_obstacle(new_square)
        Arena.log(f"Obstacle at square {new_square}")
        self.log_entities_matrix()

    def get_square_properties(self, square):
        (x, y) = square
        return self._tm.get_tile_properties(x, y)

    def _fetch_spawn_locations(self, locations):
        for name, world_point in locations.items():
            # Normalize the coordinates: they must be at the center of a square.
            orig_world_point            = world_point
            world_point                 = self.point( self.square(orig_world_point) )
            self._spawn_locations[name] = world_point
            Arena.log(f"Spawn Location '{name}': {orig_world_point} → {world_point}")

    def spawn_locations(self):
        return self._spawn_locations

    def spawn_location(self, name):
        try:
            return self.spawn_locations()[name]
        except KeyError:
            return None
