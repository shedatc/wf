import pygame

from pygame import Rect

from .utils import log_ex

class Camera:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    # Unit is the pixel.
    def __init__(self, surface_rect, steps):
        self.surface_rect = surface_rect                                          # pixels
        self.rect         = Rect((0, 0), pygame.display.get_surface().get_size()) # pixels
        self.rect.center  = surface_rect.center

        (self.horizontal_step, self.vertical_step) = steps

        Camera.log(f"Rectangle:      {self.rect} pixels")
        Camera.log(f"Surface:        {self.surface_rect} pixels")
        Camera.log(f"Steps:")
        Camera.log(f"    Horizontal: {self.horizontal_step} pixels")
        Camera.log(f"    Vertical:   {self.vertical_step} pixels")

        Camera._singleton = self

    def move(self, x, y):
        orig_rect = self.rect
        self.rect = orig_rect.move(x, y).clamp(self.surface_rect)
        Camera.log(f"Move: {orig_rect} → {self.rect}")

    def left(self):
        self.move(-self.horizontal_step, 0)

    def right(self):
        self.move(self.horizontal_step, 0)

    def up(self):
        self.move(0, -self.vertical_step)

    def down(self):
        self.move(0, self.vertical_step)

    def view_point(self, p):
        return self.rect.collidepoint(p)

    def screen_point(self, p):
        assert self.view_point(p), "Point {p} is not visible through the camera"
        (x, y) = p
        return (x - self.rect.x, y - self.rect.y)
