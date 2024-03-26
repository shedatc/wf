from .utils  import log_ex

# A navigation beacon is a square in the arena that is not an obstacle.
class NavBeacon:

    def log(msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        from .arena import Square
        self.square     = Square(0, 0)
        self.is_enabled = False

    def try_move(self, square):
        if square.is_obstacle():
            self.square     = None
            self.is_enabled = False
            NavBeacon.log(f"Square {square}, point {square.point()} is an obstacle")
        else:
            self.square     = square
            self.is_enabled = True
            NavBeacon.log(f"Moved to square {square}, point {square.point()}")
        return self.is_enabled

    def from_mouse(self):
        from .arena import Square
        square = Square(0, 0).from_mouse()
        self.try_move(square)
        return self

    def __str__(self):
        return str(self.square)
