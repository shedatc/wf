from .Arena  import Arena
from .Camera import Camera
from .Mouse  import Mouse
from .Square import Square
from .utils  import log_ex

# A point somewhere in the arena.
# A point is said to be visible if in the camera range.
class Point:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

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
