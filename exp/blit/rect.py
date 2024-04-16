from pygame         import K_ESCAPE, K_q, init, KEYUP, QUIT, Rect
from pygame.display import flip, set_mode
from pygame.draw    import rect as draw_rect
from pygame.event   import get  as events_get
from pygame.font    import Font
from pygame.mouse   import get_pos     as mouse_pos
from pygame.mouse   import set_pos     as mouse_set_pos
from pygame.mouse   import set_visible as mouse_set_visible
from pygame.time    import Clock

RED   = (200,   0,   0)
GREEN = (0,   200,   0)
BLUE  = (0,     0, 200)
BLACK = (0,     0,   0)
WHITE = (250, 250, 250)

font = None

def text(msg, point, color=BLACK):
    global font
    if font is None:
        font = Font(None, 15)
    text_surf = font.render(msg,
                            True,  # antialias
                            color,
                            WHITE) # background
    global screen
    screen.blit(text_surf, point)

def draw_point(name, position, color=BLACK, stats=False):
    rect        = Rect((0, 0), (5, 5))
    rect.center = position
    global screen
    draw_rect(screen, color, rect)
    (tx, ty) = rect.bottomright
    tx += 10
    if stats:
        text(f"{name}: {position}", (tx, ty), color=color)
    else:
        text(f"{name}", (tx, ty), color=color)

class Sprite:

    def __init__(self, position):
        self.position = position
        self.rect     = Rect(position, (20, 10))
        print(f"sprite: {self.rect}")

    def blit(self):
        global screen
        draw_rect(screen, RED, self.rect, width=1)

def main(argv=[]):
    init()
    global screen
    screen = set_mode((800, 600))
    mouse_set_visible(False)
    mouse_set_pos((400, 270))

    clock = Clock()

    a  = Rect(( 50,  50), (700, 450))
    b  = Rect((400, 300), (200, 400))
    cb = b

    while True:
        events = events_get()
        for event in events:
            if event.type == QUIT:
                return 0
            elif event.type == KEYUP:
                if event.key in [K_ESCAPE, K_q]:
                    return 0

        b.center = mouse_pos()
        cb       = a.clip(b)

        clock.tick(60)

        screen.fill(WHITE)

        draw_rect(screen, BLUE, a, width=2)
        (x, y) = a.topleft
        text("A", (x - 10, y - 10), color=BLUE)

        if cb:
            color = GREEN
        else:
            color = RED
        draw_rect(screen, color, b, width=1)
        draw_rect(screen, color, cb)
        (x, y) = b.topleft
        text("B", (x - 10, y - 10), color=color)

        y = 530
        for label, value in [("A colliderect B:", a.colliderect(b)),
                             ("A contains B:",    a.contains(b)),    ]:
            if value:
                color = GREEN
            else:
                color = RED
            text(label, (300, y)); text(str(value), (400, y), color=color)
            y += 10

        text(f"Keys:",           (30, 530))
        text(f"    Q/ESC",       (30, 540)); text(f"Exit", (130, 540))

        flip()

    # NOTREACHED

if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv) )
