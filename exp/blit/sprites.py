from operator import attrgetter

from os import getcwd

import pygame.image

from pygame         import K_DOWN, K_ESCAPE, K_F1, K_LEFT, K_RIGHT, K_q, K_UP
from pygame         import init, KEYUP, MOUSEBUTTONUP, QUIT, Rect
from pygame.draw    import rect as draw_rect
from pygame.display import flip, set_mode
from pygame.event   import get  as events_get
from pygame.font    import Font
from pygame.mouse   import get_pos     as mouse_pos
from pygame.mouse   import set_visible as mouse_set_visible

BLACK = (0,     0,   0)
BLUE  = (0,     0, 200)
GREEN = (0,   200,   0)
GREY  = (128, 128, 128)
RED   = (200,   0,   0)
WHITE = (250, 250, 250)

font      = None
log_level = 1
text_y    = None

def log(msg, prefix="", level=1):
    global log_level
    if log_level < level:
        return
    if type(prefix) is str:
        prefix = prefix + "   "
    else:
        prefix = f"{type(prefix).__name__}   "
    print(f"{prefix:>20s}{msg}")

def text(msg, position, color=BLACK, nl=False):
    global font
    if font is None:
        font = Font(None, 15)
    text_surf = font.render(msg,
                            True,  # antialias
                            color,
                            WHITE) # background
    if type(position) is not tuple:
        global text_y
        assert text_y is not None
        position = (position, text_y)
        if nl:
            text_y += 10
    Screen.singleton().screen_blit(text_surf, position)

def image_load(path):
    surface = pygame.image.load(path)
    surface.convert()
    surface.convert_alpha()
    return surface

class Screen:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    def __init__(self):
        size = (800, 600)

        self.surface = set_mode(size)
        rect         = self.surface.get_rect()
        self.size    = rect.size
        log(f"Size: {rect.size} ({size} requested)", prefix=self)

        self.blit_count = 0

    def reset(self, color=BLACK):
        log(f"Reset screen", level=2, prefix=self)
        self.blit_count = 0
        self.surface.fill(color)

    def _blit_needed(self, source_surface, screen_point, source_rect=None):
        if source_rect is None:
            source_rect = source_surface.get_rect()
        screen_rect       = self.surface.get_rect()
        dest_rect         = Rect(screen_point, source_rect.size)
        clipped_dest_rect = screen_rect.clip(dest_rect)
        return clipped_dest_rect

    def screen_blit(self, source_surface, screen_point, source_rect=None):
        if source_rect is None:
            log(f"Blit {source_surface} to screen at {screen_point}", level=2, prefix=self)
        else:
            log(f"Blit {source_rect} from {source_surface} to screen at {screen_point}", level=2, prefix=self)

        if not self._blit_needed(source_surface, screen_point, source_rect=source_rect):
            return
        self.surface.blit(source_surface, screen_point, area=source_rect)
        self.blit_count += 1

class Sprite:

    def __init__(self, name, position, image_path):
        self.name     = name # f"{name}@{hex(id(self))}"
        self.position = position

        with open(image_path, "rb") as f:
            self.surface = image_load(f)

        size = self.surface.get_size()

        # Log some data
        global log_level
        if log_level >= 1:
            log(f"Sprite '{name}':",                      level=1, prefix=self)
            log(f"    Position:   {position}",            level=1, prefix=self)
            log(f"    Image Path: {image_path}",          level=1, prefix=self)
            log(f"    Size:       {size[0]}x{size[1]}px", level=1, prefix=self)

    def __getattr__(self, name):
        if name == "x":
            return self.position[0]
        elif name == "y":
            return self.position[1]
        else:
            raise AttributeError()

    def blit(self):
        screen = Screen.singleton().surface

        # Surface
        r = Rect((0, 0), self.surface.get_size())
        r.center = self.position
        screen.blit(self.surface, r)

        # Name
        if False:
            text(self.name, (r.left - 10, r.top - 10))

        # Position
        if True:
            (x, y) = self.position
            r = Rect((x-2, y-2), (5, 5))
            draw_rect(screen, WHITE, r)
            r = Rect((x-1, y-1), (3, 3))
            draw_rect(screen, BLACK, r)

def main(argv=[]):
    log(f"Current Working Directory: {getcwd()}", level=1, prefix="main")

    init()
    Screen.singleton()
    mouse_set_visible(True)

    sort_keys = {
        "y":  attrgetter("y"),
        "yx": attrgetter("y", "x"),
    }
    sort_keys_names = list(sort_keys.keys())
    selected_sort_key_index = 0

    square                = Sprite("Square", (250, 250), "iso-square.png")
    slab                  = Sprite("Slab",   (400, 300), "iso-slab.png")
    cube                  = Sprite("Cube",   (500, 270), "iso-cube.png")
    sprites               = [square, slab, cube]
    selected_sprite_index = 0

    screen = Screen.singleton()

    global log_level
    while True:
        events = events_get()
        for event in events:
            if event.type == QUIT:
                return 0
            elif event.type == KEYUP:
                if event.key in [K_ESCAPE, K_q]:
                    return 0
                elif event.key == K_F1:
                    log_level = (log_level + 1) % 4
                elif event.key == K_UP:
                    selected_sort_key_index = (selected_sort_key_index - 1) % len(sort_keys)
                elif event.key == K_DOWN:
                    selected_sort_key_index = (selected_sort_key_index + 1) % len(sort_keys)
                elif event.key == K_LEFT:
                    selected_sprite_index = (selected_sprite_index - 1) % len(sprites)
                elif event.key == K_RIGHT:
                    selected_sprite_index = (selected_sprite_index + 1) % len(sprites)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: # Left Click
                    pass
                else:                 # Middle/Right Click
                    pass

        selected_sprite          = sprites[selected_sprite_index]
        selected_sprite.position = mouse_pos()

        screen.reset(WHITE)

        selected_sort_keys_name = sort_keys_names[selected_sort_key_index]
        sk                      = sort_keys[selected_sort_keys_name]
        sorted_sprites          = sorted(sprites, key =sk)
        for sprite in sorted_sprites:
            sprite.blit()

        global text_y
        text_y = 30
        text("Counters:",   30, nl=True)
        text("    Sprite:", 30); text(f"{len(sprites)}",      130, nl=True)
        text("    Blit:",   30); text(f"{screen.blit_count}", 130, nl=True)

        text_y = 30
        text("Selected:", 230, nl=True)
        text("Sprite:",   250); text(selected_sprite.name,    350, nl=True)
        text("Sort Key:", 250); text(selected_sort_keys_name, 350, nl=True)

        text_y = 130
        text("Log Level:", 30); text(f"{log_level}", 130)

        text_y = 530
        text(f"Keys:",         30, nl=True)
        text("    Q/ESC",      30); text("Exit",                   200, nl=True)
        text("    F1",         30); text("Increase log verbosity", 200, nl=True)
        text("    LEFT/RIGHT", 30); text("Select another sprite",  200, nl=True)

        flip()

    # NOTREACHED

if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv) )
