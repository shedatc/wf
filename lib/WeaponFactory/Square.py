from .utils import log_ex

# A square in the arena.
class Square:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, u, v):
        (self.u, self.v)   = (int(u), int(v))
        (self.pu, self.pv) = (None, None)

    def __str__(self):
        return f"[{self.u}, {self.v}]"

    def __eq__(self, other_square):
        return self.u == other_square.u and self.v == other_square.v

    def uv(self):
        return (self.u, self.v)

    def move(self, u, v):
        (self.pu, self.pv) = (self.u, self.v)
        (self.u, self.v)   = (u, v)
        return self

    # Tell if the other square is next to this one. A square is considered next
    # to itself.
    def is_next_to(self, other_square):
        du = abs(self.u - other_square.u)
        dv = abs(self.v - other_square.v)
        return du <= 1 and dv <= 1
