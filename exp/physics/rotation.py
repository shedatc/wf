from pygame         import K_ESCAPE, K_q, K_RETURN, K_SPACE, init, KEYUP, KMOD_SHIFT, MOUSEBUTTONUP, QUIT, Rect
from pygame.display import flip, set_mode
from pygame.draw    import arc  as draw_arc
from pygame.draw    import line as draw_line
from pygame.draw    import rect as draw_rect
from pygame.event   import get  as events_get
from pygame.font    import Font
from pygame.key     import get_mods
from pygame.math    import Vector2
from pygame.mouse   import get_pos     as mouse_pos
from pygame.mouse   import set_visible as mouse_set_visible
from pygame.time    import Clock

from math import asin, degrees, fabs, pi, radians

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
    if type(v) is Vector2:
        (vx, vy) = v.xy
    else:
        (vx, vy) = v
    (px, py) = p
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

class Rotation:

    CW  = -1 # Clockwize
    CCW =  1 # Counterclockwize

    def __init__(self, entity, orig_angle, angular_speed):
        self.angular_speed  = angular_speed # °/ms
        self.current_angle  = orig_angle    # °
        self.direction      = Rotation.CCW  # CW or CCW
        self.entity         = entity
        self.target_angle   = orig_angle    # °

    def _angle_from_vector(self, v):
        u        = v / v.length()
        (_, uy)  = u.xy
        angle    = asin(fabs(uy))
        (vx, vy) = v.xy
        if vx >= 0.0:
            if vy >= 0.0:
                angle = 2*pi - angle
            else: # vy < 0
                pass
        else: # vx < 0.0
            if vy >= 0.0:
                angle = pi + angle
            else: # vy < 0.0
                angle = pi - angle
        return degrees(angle)

    def look_from(self, current):
        (ex, ey)           = self.entity.position
        (cx, cy)           = current
        ec                 = Vector2(cx - ex, cy - ey)
        self.current_angle = self._angle_from_vector(ec)

    def look_at(self, target):
        (ex, ey)          = self.entity.position
        (tx, ty)          = target
        et                = Vector2(tx - ex, ty - ey)
        self.target_angle = self._angle_from_vector(et)

    def update(self):
        if self.target_angle >= self.current_angle:
            ccw = self.target_angle - self.current_angle
            cw  = 360 - ccw
        else:
            cw  = self.current_angle - self.target_angle
            ccw = 360 - cw
        if ccw <= cw:
            self.direction = Rotation.CCW
            if self.target_angle == 0.0:
                self.target_angle = 360.0
        else:
            self.direction = Rotation.CW
            if self.target_angle == 360.0:
                self.target_angle = 0.0

        # Handle the 0° == 360° aspect.
        if self.direction == Rotation.CCW:
            if self.target_angle == 0.0:
                self.target_angle = 360.0
        else: # self.direction == Rotation.CW
            if self.target_angle == 360.0:
                self.target_angle = 0.0

    def is_done(self):
        return self.target_angle == self.current_angle

    def add_time(self, t):
        assert self.current_angle != self.target_angle
        new_angle      = self.current_angle + t * self.direction * self.angular_speed
        i              = min(new_angle, self.current_angle)
        a              = max(new_angle, self.current_angle)
        target_crossed = i <= self.target_angle  and self.target_angle <= a

        if target_crossed:
            self.current_angle = self.target_angle
            print(f"| {new_angle:.2f} | {i:.2f} | {a:.2f} | {target_crossed} | {self.current_angle:.2f} | {self.target_angle:.2f}")
            assert self.is_done()
            return
        self.current_angle = new_angle % 360
        print(f"| {new_angle:.2f} | {i:.2f} | {a:.2f} | {target_crossed} | {self.current_angle:.2f} | {self.target_angle:.2f}")

    def blit(self):
        rect        = Rect((0, 0), (200, 200))
        rect.center = self.entity.position
        if self.direction == Rotation.CCW:
            draw_arc(screen, GREEN, rect, radians(self.current_angle), radians(self.target_angle), width=4)
            draw_arc(screen, RED,   rect, radians(self.target_angle),  radians(self.current_angle))
        else: # self.direction == Rotation.CW
            draw_arc(screen, RED,   rect, radians(self.current_angle), radians(self.target_angle))
            draw_arc(screen, GREEN, rect, radians(self.target_angle),  radians(self.current_angle), width=4)

        if self.target_angle >= self.current_angle:
            ccw = self.target_angle - self.current_angle
            cw  = 360 - ccw
        else:
            cw  = self.current_angle - self.target_angle
            ccw = 360 - cw

        i = 30
        text(f"Angles:",      (30, i+30))
        text(f"    Target:",  (30, i+40)); text(f"{self.target_angle:.2f}° {radians(self.target_angle):.2f} rad",   (130, i+40))
        text(f"    Current:", (30, i+50)); text(f"{self.current_angle:.2f}° {radians(self.current_angle):.2f} rad", (130, i+50))
        if self.direction == Rotation.CCW:
            text(f"    CCW:", (30, i+60), color=GREEN); text(f"{ccw:.2f}° {radians(ccw):.2f} rad", (130, i+60), color=GREEN)
            text(f"    CW:",  (30, i+70), color=RED);   text(f"{cw:.2f}° {radians(cw):.2f} rad",   (130, i+70), color=RED)
            d = "CCW"
        else:
            text(f"    CCW:", (30, i+60), color=RED);   text(f"{ccw:.2f}° {radians(ccw):.2f} rad", (130, i+60), color=RED)
            text(f"    CW:",  (30, i+70), color=GREEN); text(f"{cw:.2f}° {radians(cw):.2f} rad",   (130, i+70), color=GREEN)
            d = "CW"
        text(f"Angular Speed:", (30, i+80)); text(f"{self.angular_speed:.2f}°/ms", (130, i+80))
        text(f"Direction:",     (30, i+90)); text(f"{d} ({self.direction})",       (130, i+90))

def main(argv=[]):
    init()
    global screen
    screen = set_mode((800, 600))
    (screen_width, screen_height) = screen.get_size()
    mouse_set_visible(True)

    clock = Clock()

    # Gather data.
    print("| new_angle | i | a | target_crossed | current_angle | target_angle")
    print("|----")

    e              = Entity((screen_width // 2, screen_height // 2))
    r              = Rotation(e, 0, 0.03)
    current_vector = Vector2(250, 0)
    target_vector  = None
    is_playing     = False
    while True:
        events = events_get()
        for event in events:
            if event.type == QUIT:
                return 0
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    is_playing = not is_playing
                elif event.key == K_RETURN:
                    is_playing = not is_playing
                elif event.key in [K_ESCAPE, K_q]:
                    return 0
            elif event.type == MOUSEBUTTONUP:
                is_playing = False
                if event.button == 1:
                    if get_mods() & KMOD_SHIFT:
                        target = (0.75 * screen_width, screen_height // 2)
                    else:
                        target = mouse_pos()
                    (ex, ey)      = e.position
                    (tx, ty)      = target
                    target_vector = Vector2(tx - ex, ty - ey)
                    r.look_at(target)
                else:
                    current        = mouse_pos()
                    (ex, ey)       = e.position
                    (cx, cy)       = current
                    current_vector = Vector2(cx - ex, cy - ey)
                    r.look_from(current)
                r.update()

        t = clock.tick(10)
        if r.is_done():
            is_playing = False
        if is_playing and t > 0:
            a = r.current_angle
            r.add_time(t)
            da = a - r.current_angle
            current_vector.rotate_ip(da)

        screen.fill(WHITE)

        if is_playing:
            text(f"PLAYING…", (30, 20))
        draw_point("Entity", e.position)
        draw_vector(e.position, Vector2(370, 0), color=BLUE, width=1, name="0°")
        draw_vector(e.position, current_vector, color=BLACK, width=1, name="Current")
        if target_vector is not None:
            draw_vector(e.position, target_vector,  color=BLACK, width=2, name="Target")
        r.blit()

        text(f"Keys:",                (30, 500))
        text(f"    SPACE",            (30, 510)); text(f"Play the rotation",             (230, 510))
        text(f"    LEFT CLICK",       (30, 520)); text(f"Move the target angle",         (230, 520))
        text(f"    SHIFT+LEFT CLICK", (30, 530)); text(f"Move the target angle to 360°", (230, 530))
        text(f"    RIGHT CLICK",      (30, 540)); text(f"Move the current angle",        (230, 540))
        text(f"    Q/ESC",            (30, 550)); text(f"Exit",                          (230, 550))

        flip()

    # NOTREACHED

if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv) )
