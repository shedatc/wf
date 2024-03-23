from math import sqrt

class Vector:

    def __init__(self, x, y):
        self._x      = x
        self._y      = y
        self._length = None

    def __str__(self):
        return f"({self._x}, {self._y})"

    # Compute the length (a.k.a., magnitude).
    def length(self):
        if self._length is None:
            self._length = sqrt(self._x * self._x + self._y * self._y)
        return self._length

    # Compute the corresponding unit vector.
    def unit(self):
        l = max(1, self.length())
        return Vector(self._x / l, self._y / l)

    def xy(self):
        return (self._x, self._y)

    def invert(self):
        self._x = -self._x
        self._y = -self._y
        return self

    def scale(self, s):
        self._x *= s
        self._y *= s
        return self
