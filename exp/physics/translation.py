from pygame         import K_ESCAPE, K_q, K_SPACE, init, KEYUP, MOUSEBUTTONUP, QUIT, Rect
from pygame.display import flip, set_mode
from pygame.draw    import line as draw_line
from pygame.draw    import rect as draw_rect
from pygame.event   import get  as events_get
from pygame.font    import Font
from pygame.math    import Vector2
from pygame.mouse   import get_pos     as mouse_pos
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
    rect = Rect((0, 0), (5, 5))
    rect.center = position
    global screen
    draw_rect(screen, color, rect)
    (tx, ty) = rect.bottomright
    tx += 10
    if stats:
        text(f"{name}: {position}", (tx, ty), color=color)
    else:
        text(f"{name}", (tx, ty), color=color)

def draw_vector(p, v, name=None, color=GREEN, width=1, stats=False):
    if type(p) is Vector2:
        (px, py) = p.xy
    else:
        (px, py) = p
    if type(v) is Vector2:
        (vx, vy) = v.xy
    else:
        (vx, vy) = v
    global screen
    draw_line(screen, color, p, (px + vx, py + vy), width=width)
    rect = Rect((0, 0), (5, 5))
    rect.center = (px + vx, py + vy)
    draw_rect(screen, color, rect)
    if name is None:
        return
    (tx, ty) = rect.bottomright
    tx += 10
    if stats:
        text(f"{name}: {v.xy}", (tx, ty), color=color)
        text(f"     len: {v.length():.2f}", (tx, ty + 10), color=color)
    else:
        text(f"{name}", (tx, ty), color=color)

class Entity:

    def __init__(self, position):
        self.position = position

    # Shift position by the given offset.
    def shift(self, offset):
        (ox, oy)      = offset
        (x, y)        = self.position
        self.position = (x + ox, y + oy)

class Translation:

    def __init__(self, entity, speed):
        self.speed           = speed # px/ms
        self.entity          = entity
        self.target_position = entity.position
        self.step_vectors    = []

    def move_to(self, position):
        self.target_position = position
        self.orig_position   = self.entity.position
        self.step_vectors.clear()

    def is_done(self):
        return self.entity.position == self.target_position

    def add_time(self, t):
        assert not self.is_done()

        (tx, ty)           = self.target_position
        (ex, ey)           = self.entity.position
        translation_vector = Vector2(tx - ex, ty - ey)
        total_distance     = translation_vector.length()
        step_vector        = (translation_vector / total_distance) * (self.speed * t)
        step_distance      = step_vector.length()

        if step_distance < total_distance:
            self.entity.shift( step_vector.xy )
            self.step_vectors.append(step_vector)
        else:
            self.entity.position = self.target_position

    def blit(self):
        (tx, ty)           = self.target_position
        (ex, ey)           = self.entity.position
        translation_vector = Vector2(tx - ex, ty - ey)
        total_distance     = translation_vector.length()

        i = 30
        text(f"Speed:",              (30, i+30)); text(f"{self.speed:.2f} px/ms",                                   (130, i+30))
        text(f"Translation Vector:", (30, i+40)); text(f"({translation_vector.x:.2f}, {translation_vector.y:.2f})", (130, i+40))
        text(f"Total distance:",     (30, i+50)); text(f"{total_distance:.2f} px",                                  (130, i+50))

        if self.target_position == self.entity.position:
            return

        if self.step_vectors == []:
            target_vector = Vector2(self.target_position) - Vector2(self.entity.position)
            draw_vector(self.entity.position, target_vector, color=BLACK, width=2, name="Target")
            return

        text(f"Step Vectors:", (30, i+60), color=RED)
        p = self.orig_position
        v = 0
        for step_vector in self.step_vectors:
            ty     = i+70 + v*10
            (x, y) = step_vector.xy
            l      = step_vector.length()
            text(f"    #{v}", (30, ty), color=RED); text(f"({x:.2f}, {y:.2f}) len: {l:.2f} px", (130, ty), color=RED)
            draw_vector(p, step_vector, color=RED)
            p += step_vector
            v += 1
        draw_point("Target", self.target_position)

def main(argv=[]):
    init()
    global screen
    screen = set_mode((800, 600))
    (screen_width, screen_height) = screen.get_size()
    mouse_set_visible(True)

    clock = Clock()

    e          = Entity((screen_width // 2, screen_height // 2))
    tr         = Translation(e, 0.07)
    is_playing = False
    while True:

        events = events_get()
        for event in events:
            if event.type == QUIT:
                return 0
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    is_playing = not is_playing
                elif event.key in [K_ESCAPE, K_q]:
                    return 0
            elif event.type == MOUSEBUTTONUP:
                is_playing = False
                if event.button == 1:
                    tr.move_to( mouse_pos() )

        t = clock.tick(10)
        if tr.is_done():
            is_playing = False
        if is_playing and t > 0:
            tr.add_time(t)

        screen.fill(WHITE)

        if is_playing:
            text(f"PLAYING…", (30, 20))
        tr.blit()
        draw_point("Entity", e.position)

        text(f"Keys:",           (30, 500))
        text(f"    SPACE",       (30, 510)); text(f"Play the translation",     (130, 510))
        text(f"    LEFT CLICK",  (30, 520)); text(f"Move the target position", (130, 520))
        text(f"    Q/ESC",       (30, 530)); text(f"Exit",                     (130, 530))

        flip()

    # NOTREACHED

if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv) )
