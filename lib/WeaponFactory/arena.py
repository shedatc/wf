import numpy  as np
import pygame

from pygame import Rect

from .const      import OBSTACLE, WALKABLE
from .const      import SQUARE_SIZE, TILE_WIDTH, TILE_HEIGHT, TILE_SQUARE_SIZE
from .input      import Mouse
from .navigation import Compass
from .resources  import Resources
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
        (screen_width, screen_height) = pygame.display.get_surface().get_size()
        Camera.log(f"screen={sz((screen_width, screen_height))}")

        a           = Arena.singleton()
        self.u      = a.width // 2 - screen_width // TILE_WIDTH // 2
        self.v      = 0
        self.width  = screen_width  // TILE_WIDTH
        self.height = screen_height // TILE_HEIGHT
        self.lu     = a.width  - self.width  - 1
        self.lv     = a.height - self.height - 1
        Camera.log(f"luv=({self.lu}, {self.lv})")

        self.show()

    def squares(self):
        return Rect(self.u, self.v, self.width, self.height)

    def show(self, prefix=None):
        if prefix is None:
            Camera.log(f"squares={self.squares()}")
        else:
            Camera.log(f"{prefix}: squares={self.squares()}")

    def left(self):
        if self.u >= 1:
            self.u -= 2
            self.show("left")

    def right(self):
        if self.u <= self.lu:
            self.u += 2
            self.show("right")

    def up(self):
        if self.v >= 1:
            self.v -= 2
            self.show("up")

    def down(self):
        if self.v <= self.lv:
            self.v += 2
            self.show("down")

    def move(self, u, v):
        (screen_width, screen_height) = pygame.display.get_window_size()
        self.u                        = min(screen_width  - self.width,  max(0, u))
        self.v                        = min(screen_height - self.height, max(0, v))

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
        Arena.log(f"name={self.name} square={SQUARE_SIZE}x{SQUARE_SIZE}")

        # Tilemap
        self.tm                   = Tilemap(self.name)
        (self.width, self.height) = self.tm.map_size

        # Strategic View
        if False:
            sv_path               = Resources.locate("image", f"{self.name}-sv.png")
            self.sv               = pygame.image.load(sv_path)
            (sv_width, sv_height) = self.sv.get_size()
            Arena.log(f"sv: path={sv_path} size={sv_width}x{sv_height}")
            assert sv_width  == self.width,  "SV image width must match tilemap width"
            assert sv_height == self.height, "SV image height must match tilemap height"

        # Obstacles:
        self.obstacles_matrix = [[WALKABLE] * self.width for i in range(self.height)]
        for v in range(self.height):
            for u in range(self.width):
                if self.tm.is_obstacle(u, v, 0):
                    self.obstacles_matrix[v][u] = OBSTACLE
        # self.log_obstacles_matrix()

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
        return self.entities_matrix[v][u]

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

    def get_tilemap(self):
        return Arena.singleton().tm

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

    def _surface(self, surface):
        return self.surface

    def blit_tactical(self, surface):
        # ArenaView.log(f"blit")
        tm = self.get_tilemap()
        for level in range(tm.level_count):
            tm.blit_level(Camera.singleton().squares(), level, surface)

        Region.singleton().blit(surface)

    def blit_strategic(self, surface):

        # Blit the view itself.
        (screen_width, screen_height) = pygame.display.get_window_size()
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

        (screen_width, screen_height) = pygame.display.get_window_size()
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

    def log(msg):
        log_ex(msg, category="Point")

    def __init__(self, x, y):
        if __debug__:
            (screen_width, screen_height) = pygame.display.get_window_size()
            if 0 > x or x > screen_width*SQUARE_SIZE-1:
                raise AssertionError()
            if 0 > y or y > screen_height*SQUARE_SIZE-1:
                raise AssertionError()
        (self.x, self.y) = (x, y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other_point):
        return self.x == other_point.x and self.y == other_point.y

    def copy(self):
        return Point(self.x, self.y)

    def pos(self):
        return (self.x, self.y)

    def mat(self):
        return np.array([(self.x,),
                         (self.y,)])

    def transform(self, t):
        m                = np.matmul(t, self.mat())
        (self.x, self.y) = (m[0][0], m[1][0])
        return self

    # FIXME Use a matrix transform.
    def translate(self, v):
        (vx, vy)         = v
        (self.x, self.y) = (self.x + vx, self.y + vy)
        return self

    # Rotate at 45°, then scale (1, 0.5).
    def to_iso(self):
        t = np.array([(1,   -1),
                      (0.5,  0.5)])
        return self.transform(t)

    # Scale (1, 2), then rotate -45°.
    def to_ortho(self):
        t = np.array([( 0.5, 1),
                      (-0.5, 1)])
        return self.transform(t)

    # Return the square containing the point.
    def square(self):
        if True:
            return Square(self.x // TILE_WIDTH, self.y // TILE_HEIGHT)
        else:
            return Square(self.x // SQUARE_SIZE, self.y // SQUARE_SIZE)

    # Move the point to the top left corner of the square it belong to.
    # FIXME Use a matrix tranform.
    def to_square(self):
        (self.x,  self.y) = (self.x // (TILE_SQUARE_SIZE) * (TILE_SQUARE_SIZE),
                             self.y // (TILE_SQUARE_SIZE) * (TILE_SQUARE_SIZE))
        return self

    def to_tile(self):
        return self.to_ortho().to_square().to_iso().translate((-TILE_WIDTH, 0))

    # Return the point in screen coordinates.
    def screen(self):
        assert self.is_visible()
        c = Camera.singleton()
        if True:
            return Point(self.x - (c.u * TILE_WIDTH),
                         self.y - (c.v * TILE_HEIGHT))
        else:
            return Point(self.x - (c.u * SQUARE_SIZE),
                         self.y - (c.v * SQUARE_SIZE))

    # Move to the coordinates pointed by the mouse.
    def from_mouse(self):
        (mx, my) = Mouse.get_coords()
        c        = Camera.singleton()
        if True:
            self.x = c.u * TILE_WIDTH  + mx
            self.y = c.v * TILE_HEIGHT + my
        else:
            self.x = c.u * SQUARE_SIZE + mx
            self.y = c.v * SQUARE_SIZE + my
        return self

    # Tell if the point is visible from current camera's position.
    def is_visible(self):
        return self.square().is_visible()

# A square in the arena.
class Square:

    def log(msg):
        log_ex(msg, category="Square")

    def __init__(self, u, v):
        u = int(u)
        v = int(v)
        if __debug__:
            (screen_width, screen_height) = pygame.display.get_window_size()
            if 0 > u or u > screen_width-1:
                raise AssertionError()
            if 0 > v or v > screen_height-1:
                raise AssertionError()

        (self.u, self.v)   = (u, v)
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
        (mx, my) = Mouse.get_coords()
        if True:
            (mu, mv) = (mx // TILE_WIDTH, my // TILE_HEIGHT)
        else:
            (mu, mv) = (mx // SQUARE_SIZE, my // SQUARE_SIZE)
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
        if True:
            return Point(self.u * TILE_WIDTH  + TILE_WIDTH  // 2,
                         self.v * TILE_HEIGHT + TILE_HEIGHT // 2)
        else:
            return Point(self.u * SQUARE_SIZE  + SQUARE_SIZE  // 2,
                         self.v * SQUARE_SIZE + SQUARE_SIZE // 2)

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

        if True:
            pixels = Rect((o.x - TILE_WIDTH // 2,         o.y - TILE_HEIGHT // 2),
                          (self.get_width() * TILE_WIDTH, self.get_height() * TILE_HEIGHT))
        else:
            pixels = Rect((o.x - SQUARE_SIZE // 2,         o.y - SQUARE_SIZE // 2),
                          (self.get_width() * SQUARE_SIZE, self.get_height() * SQUARE_SIZE))
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
