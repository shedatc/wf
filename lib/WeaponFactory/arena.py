import pygame

from pygame import Rect

from .const      import OBSTACLE, WALKABLE
from .input      import Mouse
from .navigation import Compass
from .assets     import Assets
from .tilemap    import Tilemap
from .utils      import Config, log_ex, sz

class Camera:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = Camera()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        (self.screen_width, self.screen_height) = pygame.display.get_surface().get_size()

        a = Arena.singleton()
        (map_width, map_height)                 = (a.width, a.height)
        (self.square_width, self.square_height) = a.square_size

        self.horizontal_step = 1 # squares
        self.vertical_step   = 1 # squares

        # Center the camera
        self.u  = map_width  // 2 - self.screen_width  // self.square_width  // 2
        self.u -= self.u % self.horizontal_step
        self.v  = map_height // 2 - self.screen_height // self.square_height // 2
        self.v -= self.v % self.vertical_step

        self.width  = self.screen_width  // self.square_width
        self.height = self.screen_height // self.square_height
        self.lu     = map_width  - self.width
        self.lv     = map_height - self.height

        Camera.log(f"Screen:              {self.screen_width}x{self.screen_height}")
        Camera.log(f"Position (uv):       [{self.u}, {self.v}]")
        Camera.log(f"Last position (luv): [{self.lu}, {self.lv}]")
        Camera.log(f"Size:                {self.width}x{self.height} squares")
        Camera.log(f"Steps:")
        Camera.log(f"    Horizontal:      {self.horizontal_step} squares")
        Camera.log(f"    Vertical:        {self.vertical_step} squares")

    def uv(self):
        return (self.u, self.v)

    def xy(self):
        return (self.u * self.square_width, self.v * self.square_height)

    def squares(self):
        return Rect(self.u, self.v, self.width, self.height)

    def left(self):
        if self.u - self.horizontal_step >= 0:
            self.u -= self.horizontal_step

    def right(self):
        if self.u + self.horizontal_step <= self.lu:
            self.u += self.horizontal_step

    def up(self):
        if self.v - self.vertical_step >= 0:
            self.v -= self.vertical_step

    def down(self):
        if self.v + self.vertical_step <= self.lv:
            self.v += self.vertical_step

    def move(self, u, v):
        (self.u, self.v) = (u, v)

    def centered_move(self, u, v):
        self.move(u - self.width  // 2,
                  v - self.height // 2)

    def view(self, square):
        assert isinstance(square, Square)
        return self.u <= square.u and square.u <= self.u + self.width \
            and self.v <= square.v and square.v <= self.v + self.height

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

class ArenaView:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = ArenaView()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        self.is_tactical       = True
        self._tactical_surface = None
        ArenaView.log(f"is_tactical={self.is_tactical}")

    def get_width(self):
        return Arena.singleton().width

    def get_height(self):
        return Arena.singleton().height

    def get_strategic_view(self):
        return Arena.singleton().sv

    def tactical(self):
        self.is_tactical = True
        return self

    def strategic(self):
        self.is_tactical = False
        return self

    def toggle(self):
        self.is_tactical = not self.is_tactical
        return self

    def update(self):
        if self.is_tactical:
            Region.singleton().update()

    def blit_tactical(self, surface):
        Arena.singleton().tm.blit(surface, Camera.singleton().squares())
        Region.singleton().blit(surface)

    def blit_strategic(self, surface):

        # Blit the view itself.
        (screen_width, screen_height) = pygame.display.get_surface().get_size()
        sv                            = self.get_strategic_view()
        (w, h)                        = sv.get_size()
        x                             = (screen_width  - w) // 2
        y                             = (screen_height - h) // 2
        surface.blit(sv, Rect((x, y), (w, h)))

        # Blit the rectangle corresponding to the camera.
        c = Camera.singleton()
        pygame.draw.rect(surface, (200, 0, 0),
                         Rect((c.u, c.v), (c.width, c.height)),
                         width=1)

        # FIXME
        return

        (screen_width, screen_height) = pygame.display.get_surface().get_size()
        for v in range(0, screen_height):
            for u in range(0, screen_width):
                entities = Arena.singleton().entities_at_square(u, v)
                if len(entities) >= 1:
                    for e in entities:
                        # FIXME
                        # if e.isSelected:
                        #     pyxel.pset(u, v, 9)
                        # else:
                        #     pyxel.pset(u, v, 13)
                        raise NotImplementedError("Must replace pyxel.pset")

    def blit(self, surface):
        if self.is_tactical:
            self.blit_tactical(surface)
        else:
            self.blit_strategic(surface)

# A point somewhere in the arena.
# A point is said to be visible if in the camera range.
class Point:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category="Point")

    def __init__(self, x, y):
        (self.x, self.y) = (x, y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other_point):
        return self.x == other_point.x and self.y == other_point.y

    def copy(self):
        return Point(self.x, self.y)

    def xy(self):
        return (self.x, self.y)

    # Return the square containing the point.
    def square(self):
        (square_width, square_height) = Arena.singleton().square_size
        return Square(self.x // square_width,
                      self.y // square_height)

    # Return the point in screen coordinates.
    def screen(self):
        assert self.is_visible()
        c                         = Camera.singleton()
        (square_width, square_height) = Arena.singleton().square_size
        return Point(self.x - (c.u * square_width),
                     self.y - (c.v * square_height))

    # Move to the coordinates pointed by the mouse.
    def from_mouse(self):
        (mx, my)                  = Mouse.screen_xy()
        c                         = Camera.singleton()
        (square_width, square_height) = Arena.singleton().square_size
        self.x = c.u * square_width  + mx
        self.y = c.v * square_height + my
        return self

    # Tell if the point is visible from current camera's position.
    def is_visible(self):
        return self.square().is_visible()

# A square in the arena.
class Square:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category="Square")

    def __init__(self, u, v):
        (self.u, self.v)   = (int(u), int(v))
        (self.pu, self.pv) = (None, None)
        self.tm            = Arena.singleton().tm

    def __str__(self):
        return f"[{self.u}, {self.v}]"

    def __eq__(self, other_square):
        return self.u == other_square.u and self.v == other_square.v

    def move(self, u, v):
        (self.pu, self.pv) = (self.u, self.v)
        (self.u, self.v)   = (u, v)
        return self

    def relative_move(self, u, v):
        c = Camera.singleton()
        return self.move(c.u + u, c.v + v)

    def can_rollback(self):
        return self.pu is not None and self.pv is not None

    def rollback(self):
        assert self.can_rollback()
        (self.u, self.v)   = (self.pu, self.pv)
        (self.pu, self.pv) = (None, None)
        return self

    def from_mouse(self):
        (square_width, square_height) = Arena.singleton().square_size
        (mx, my)                      = Mouse.screen_xy()
        (mu, mv)                      = (mx // square_width, my // square_height)
        self.relative_move(mu, mv)
        return self

    def tile_data(self):
        # FIXME
        # return pyxel.tilemap(self.tm).get(self.u, self.v)
        raise NotImplementedError("Must replace pyxel.tilemap")

    def is_obstacle(self):
        return Arena.singleton().is_obstacle(self)

    def is_visible(self):
        return Camera.singleton().view(self)

    def point(self):
        (square_width, square_height) = Arena.singleton().square_size
        return Point(self.u * square_width  + square_width  // 2,
                     self.v * square_height + square_height // 2)

    # Tell if the other square is next to this one. A square is considered next
    # to itself.
    def is_next_to(self, other_square):
        du = abs(self.u - other_square.u)
        dv = abs(self.v - other_square.v)
        return du <= 1 and dv <= 1

class Region:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = Region()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        self.start      = None
        self.end        = None
        self.is_enabled = False
        Region.log(f"start={self.start} end={self.end} is_enabled={self.is_enabled}")

    def enable(self):
        if self.is_enabled:
            Region.log("already enabled")
        else:
            self.start      = Square(0, 0).from_mouse()
            self.end        = Square(0, 0).from_mouse()
            self.is_enabled = True
            Region.log("enabled")

    # Return the entities belonging to the region. Return None if already
    # disabled.
    def disable(self):
        if self.is_enabled:
            Region.log("disabled")
            entities        = self.get_entities()
            self.start      = None
            self.end        = None
            self.is_enabled = False
            return entities
        else:
            Region.log("already disabled")
            return None

    def is_empty(self):
        self.end is None or self.start == self.end

    def update(self):
        if not self.is_enabled:
            return
        if self.end is not None:
            self.end.from_mouse()
            Region.log(f"start={self.start} end={self.end} is_enabled={self.is_enabled}")

    def get_origin(self):
        assert self.is_enabled
        s = self.start
        e = self.end
        u = min(s.u, e.u)
        v = min(s.v, e.v)
        return Square(u, v)

    def get_width(self):
        assert self.is_enabled
        return abs(self.start.u - self.end.u) + 1

    def get_height(self):
        assert self.is_enabled
        return abs(self.start.v - self.end.v) + 1

    def blit(self, surface):
        if not self.is_enabled:
            return

        # Draw the square-level region
        o  = self.get_origin().point().screen()
        Region.log(f"origin={o}")

        (square_width, square_height) = Arena.singleton().square_size
        pixels = Rect((o.x - square_width // 2,         o.y - square_height // 2),
                      (self.get_width() * square_width, self.get_height() * square_height))
        pygame.draw.rect(surface, (200, 0, 0), pixels, width=1)

    # Return the entities that are part of the region.
    def get_entities(self):
        entities = []
        o        = self.get_origin()
        a        = Arena.singleton()
        for v in range(o.v, o.v + self.get_height()):
            for u in range(o.u, o.u + self.get_width()):
                e = a.entities_at_square(u, v)
                Region.log(f"e={e} len(e)={len(e)}")
                if len(e) >= 1:
                    # If at least one entity is on the square, add only the
                    # first one to handle stacking.
                    entities.append(e[0])
        Region.log(f"entities={entities}")
        return entities
