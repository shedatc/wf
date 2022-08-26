from math import sqrt

class Vector:

    def __init__(self, x, y):
        self.x      = x
        self.y      = y
        self.length = None
        self.unit   = None

    def __str__(self):
        return f"({self.x}, {self.y})"

    # Compute the length (a.k.a., magnitude).
    def getLength(self):
        if self.length is None:
            self.length = sqrt(self.x * self.x + self.y * self.y)
        return self.length

    # Compute the corresponding unit vector.
    def getUnit(self):
        if self.unit is None:
            l = self.getLength()
            self.unit = Vector(self.x / l, self.y / l)
        return self.unit

    def scale(self, s):
        self.x *= s
        self.y *= s
        return self
