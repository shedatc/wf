import pygame

from pygame import Rect

from .Arena import Arena
from .utils import log_ex

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
        return self.u <= square.u and square.u <= self.u + self.width \
            and self.v <= square.v and square.v <= self.v + self.height
