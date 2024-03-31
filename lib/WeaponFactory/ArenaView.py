import pygame

from pygame import Rect

from .Arena  import Arena
# from .Camera import Camera
from .Region import Region
from .utils  import log_ex

class ArenaView:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = ArenaView()
        return cls._singleton

    @classmethod
    def delete_singleton(cls):
        cls._singleton = None

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        self.is_tactical       = True
        self._tactical_surface = None
        ArenaView.log(f"is_tactical={self.is_tactical}")

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
        pass
        # if self.is_tactical:
        #     Region.singleton().update()

    def blit_tactical(self, source_rect):
        Arena.singleton().blit(source_rect)
        if False:
            Region.singleton().blit(surface)

    def blit_strategic(self):
        raise NotImplementedError()

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

    def blit(self, source_rect):
        if self.is_tactical:
            self.blit_tactical(source_rect)
        else:
            self.blit_strategic()
