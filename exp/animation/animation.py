from json import loads as json_load

from math import floor

from os      import getcwd
from os.path import basename
from os.path import join as path_join

from pygame         import K_ESCAPE, K_F1, K_q, init, KEYUP, MOUSEBUTTONUP, QUIT, Rect
from pygame         import Rect
from pygame.display import flip, set_mode
from pygame.event   import get  as events_get
from pygame.font    import Font
from pygame.image   import load as pygame_image_load
from pygame.mouse   import get_pos     as mouse_pos
from pygame.mouse   import set_visible as mouse_set_visible
from pygame.time    import Clock

RED   = (200,   0,   0)
GREEN = (0,   200,   0)
BLUE  = (0,     0, 200)
BLACK = (0,     0,   0)
WHITE = (250, 250, 250)

font      = None
log_level = 1

def log(msg, prefix="", level=1):
    global log_level
    if log_level < level:
        return
    if type(prefix) is str:
        prefix = prefix + "   "
    else:
        prefix = f"{type(prefix).__name__}   "
    print(f"{prefix:>20s}{msg}")

def text(msg, point, color=BLACK):
    global font
    if font is None:
        font = Font(None, 15)
    text_surf = font.render(msg,
                            True,  # antialias
                            color,
                            WHITE) # background
    Screen.singleton().screen_blit(text_surf, point)

def conf_load(conf_path):
    with open(conf_path, "r") as cf:
        return json_load( cf.read() )

def image_load(img_path):
    return pygame_image_load(img_path)

class EngineClock:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    def __init__(self):
        self._fps = 0
        if self._fps == 0:
            log(f"FPS: ∞", prefix=self)
        else:
            log(f"FPS: {self._fps}", prefix=self)
        self._running = []
        self._paused  = []
        self.reset_clock()

    def reset_clock(self):
        self.clock = Clock()
        log(f"Reset engine clock", prefix=self, level=2)

    def register(self, task):
        assert task not in self._running, "Task already registered and currently running"
        assert task not in self._paused, "Task already registered and currently paused"
        self._paused.append(task)
        log(f"Registered paused task: {task}", prefix=self)
        return self

    def unregister(self, task):
        if task in self._running:
            self._running.remove(task)
            log(f"Unregistered running task: {task}", prefix=self)
        elif task in self._paused:
            self._paused.remove(task)
            log(f"Unregistered paused task: {task}", prefix=self)
        else:
            raise AssertionError("Unknown task")
        return self

    def pause(self, task):
        try:
            self._running.remove(task)
        except ValueError:
            assert task in self._paused, "Trying to pause a task that was not running"
        if task not in self._paused:
            self._paused.append(task)
            log(f"Paused task: {task}", prefix=self)
        else:
            log("Trying to pause a task that is already paused", prefix=self)
        return self

    def resume(self, task):
        try:
            self._paused.remove(task)
        except ValueError:
            assert task in self._running, "Trying to resume a task that was not paused"
        if task not in self._running:
            self._running.append(task)
            log(f"Resumed task: {task}", prefix=self)
        else:
            log("Trying to resume a task that is already running", prefix=self)
        return self

    # Add time to running tasks and return time (ms) since previous tick.
    def tick(self):
        if self._fps == 0:
            t = self.clock.tick()
        else:
            t = self.clock.tick(self._fps)
        if t == 0:
            return 0
        if len(self._running) == 0:
            return t
        log(f"Tick: {t} ms since previous tick", level=2, prefix=self)
        c = 0
        for task in self._running:
            assert not task.is_done()
            task.add_time(t)
            log(f"Added {t} ms to task {task}", level=2, prefix=self)
            if task.is_done():
                self.pause(task)
            c += 1
        if c > 0:
            log(f"Added {t} ms to {c} tasks", level=2, prefix=self)
        return t

    def fps(self):
        return floor( self.clock.get_fps() )

    def running_task_count(self):
        return len(self._running)

    def paused_task_count(self):
        return len(self._paused)

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

class AnimationFrame:

    def __init__(self, name, surface, rect,
                 duration=100, rotated=False, trimmed=False):
        self._rect    = rect
        self._surface = surface
        self.duration = duration # ms
        self.name     = name

        log(f"Animation Frame '{name}':", level=3, prefix=self)
        log(f"    Duration:  {duration}", level=3, prefix=self)
        log(f"    Surface:   {surface}",  level=3, prefix=self)
        log(f"    Rectangle: {rect}",     level=3, prefix=self)

        assert rotated is False, "Frame rotation is not supported"
        assert trimmed is False, "Frame trim is not supported"

    def blit_at(self, position):
        dest_rect        = self._rect.copy()
        dest_rect.center = position
        log(f"Blit {self._rect} at {position}", level=3, prefix=self)
        Screen.singleton().screen_blit(self._surface, dest_rect.topleft,
                                       source_rect=self._rect)

class AnimationState:

    def __init__(self, frames, is_loop):
        self._is_loop            = is_loop
        self._last_frame_index   = len(frames) - 1
        self.current_frame_index = 0

        self._duration  = frames[0].duration # Remaining duration of the current frame.
        self._durations = []                 # Store the duration of each frame.
        for f in frames:
            self._durations.append( f.duration )

        EngineClock.singleton().register(self)

    def __del__(self):
        EngineClock.singleton().unregister(self)

    def rewind(self):
        log(f"Rewinding…", level=3, prefix=self)
        self.current_frame_index    = 0
        self._duration = self._durations[0]

    def pause(self):
        EngineClock.singleton().pause(self)

    def resume(self):
        EngineClock.singleton().resume(self)

    def _next_frame(self):
        assert not self.is_done()
        self.current_frame_index += 1
        if self.current_frame_index <= self._last_frame_index:
            self._duration = self._durations[self.current_frame_index]
        elif self._is_loop: # and self.current_frame_index > self._last_frame_index
            self.rewind()
        log(f"Now at frame {self.current_frame_index}/{self._last_frame_index}", level=3, prefix=self)

    def is_done(self):
        return self.current_frame_index > self._last_frame_index and not self._is_loop

    # Add time to the current frame. If adding more time than necessary to
    # finish it, use this time for the next frame, etc…
    def add_time(self, t):
        assert not self.is_done()
        while t > 0 and not self.is_done():
            log(f"Adding {t} ms to frame {self.current_frame_index}/{self._last_frame_index}", level=3, prefix=self)

            assert self._duration > 0
            orig_remaining_duration = self._duration
            if t <= self._duration:
                self._duration -= t
                t                            = 0
            else: # t > self._duration
                t                           -= self._duration
                self._duration  = 0

            log(f"Added {t} ms to current frame:",                                   level=3, prefix=self)
            log(f"    {orig_remaining_duration} → {self._duration} ms", level=3, prefix=self)
            log(f"{t} ms remaining",                                                 level=3, prefix=self)

            if self._duration == 0:
                self._next_frame()
        if self.is_done():
            log(f"Animation done", level=3, prefix=self)

class Animation:

    def __init__(self, name, frames, is_loop=True):
        self._frames  = frames
        self._is_loop = is_loop
        self._state   = AnimationState(frames, is_loop)
        self.name     = name

    # Current Frame
    def _cf(self):
        return self._frames[self._state.current_frame_index]

    def __repr__(self):
        return f"<Animation '{self.name}' at frame '{self._cf().name}'>"

    def rewind(self):
        self._state.rewind()
        return self

    def pause(self):
        self._state.pause()
        return self

    def resume(self):
        self._state.resume()
        return self

    def blit_at(self, position):
        self._cf().blit_at(position)

    def copy(self):
        return Animation(self.name, self._frames, is_loop=self._is_loop)

class AnimationFactory:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def _load_spritesheet_libresprite(cls, conf):
        meta    = conf["meta"]
        app     = meta["app"]
        version = meta["version"]
        format  = meta["format"]
        image   = meta["image"]

        log(f"Application: {app}", level=1, prefix="AnimationFactory")
        log(f"Version:     {version}", level=1, prefix="AninationFactory")
        log(f"Format:      {format}", level=1, prefix="AninationFactory")

        if version != "1.0":
            raise RuntimeError("Libresprite spritesheet version not supported")
        if format not in ["I8", "RGBA8888"]:
            raise RuntimeError("Libresprite spritesheet format not supported")

        # Ignore all but the filename from the image path
        surface = image_load( path_join("animations", basename(image)) )

        if "frameTags" not in meta:
            raise RuntimeError("Missing frameTags")
        animations = {}
        for frame_tag in meta["frameTags"]:
            name      = frame_tag["name"]
            direction = frame_tag["direction"]
            start     = frame_tag["from"]
            end       = frame_tag["to"]
            if direction != "forward":
                raise RuntimeError("Direction not supported")
            frames = []
            for f in range(start, end+1):
                frame           = conf["frames"][f]
                frame_rect = Rect((frame["frame"]["x"], frame["frame"]["y"]),
                                  (frame["frame"]["w"], frame["frame"]["h"]))
                animation_frame = AnimationFrame(f"{name} {f}/{end}",
                                                 surface,
                                                 frame_rect,
                                                 duration=frame["duration"])
                frames.append(animation_frame)

            log(f"Animation '{name}':", level=1, prefix="AninationFactory")
            log(f"    Direction: {direction}", level=1, prefix="AninationFactory")
            log(f"    Frames:    {start}..{end}, {len(frames)} frames", level=1, prefix="AninationFactory")

            animations[name] = Animation(name, frames)

        return (surface, animations)

    def __init__(self):
        self._animations = {}
        self.load_count  = 0

    def load(self, group_name):
        if group_name in self._animations:
            log(f"Copying animation group '{group_name}'…", level=1, prefix=self)
            (surface, animations) = self._animations[group_name]
            animations_copy       = {}
            for name, animation in animations.items():
                animations_copy[name] = animation.copy()
            return (surface, animations_copy)

        conf_path = path_join("animations", group_name + ".json")
        log(f"Loading animation group '{group_name}' from {conf_path}…", level=1, prefix=self)
        conf = conf_load(conf_path)
        spritesheet_load = None
        if "meta" in conf and "app" in conf["meta"]:
            app = conf["meta"]["app"]
            if app == "https://github.com/LibreSprite/LibreSprite/":
                spritesheet_load = AnimationFactory._load_spritesheet_libresprite
        if spritesheet_load is None:
            raise RuntimeError("No loader for spritesheet")
        (surface, animations) = spritesheet_load(conf)
        assert surface is not None, "Missing surface"
        assert len(animations) > 0, "Missing animations"
        self._animations[group_name] = (surface, animations)
        self.load_count += 1

        return (surface, animations)

class AnimationPlayer:

    def __init__(self, group_name, select="Idle"):
        self._current = None
        self.visible  = False

        (self.surface, self.animations) = AnimationFactory.singleton().load(group_name)
        self.select(select)

    def show(self):
        self.visible = True
        return self

    def hide(self):
        self.visible = False
        return self

    def select(self, name):
        orig_name = None
        if self._current is not None:
            orig_name = self.current.name
            self._current.pause()
        self.current = self.animations[name].rewind().resume()
        if orig_name is None:
            log(f"Now playing animation '{name}'", level=1, prefix=self)
        else:
            log(f"Now playing animation '{orig_name}' → '{name}'", level=1, prefix=self)
        return self

    def pause(self):
        self.current.pause()
        return self

    def resume(self):
        self.current.resume()
        return self

    def blit_at(self, position):
        if not self.visible:
            return
        self.current.blit_at(position)

class Sprite:

    def __init__(self, name, position, conf_path=None):
        if conf_path is None:
            conf_path = path_join(name, "sprite.json")
        log(f"Loading sprite from {conf_path}…", level=1, prefix=self)
        conf = conf_load(conf_path)

        self.name     = f"{name}@{hex(id(self))}"
        self.position = position

        self._animations      = {}
        self._animation_order = []
        for animation_config in conf["animations"]:
            offset           = animation_config["offset"]
            name             = animation_config["name"]
            select           = animation_config["select"]
            enable           = animation_config["enable"]
            animation_player = AnimationPlayer(name, select=select)
            if enable:
                animation_player.resume()
                animation_player.show()
                e = "enabled"
            else:
                e = "disabled"
            o = len(self._animation_order)
            self._animations[name] = {
                "offset":           offset,
                "animation_player": animation_player,
                "enable":           enable
            }
            self._animation_order.append(name)

        # Log some data
        global log_level
        if log_level >= 1:
            log(f"Sprite '{name}':", level=1, prefix=self)
            log(f"    Position: {position}", level=1, prefix=self)
            log(f"    Animations:", level=1, prefix=self)
            o = 0
            for name, a in self._animations.items():
                enable = a["enable"]
                offset = a["offset"]
                select = a["animation_player"].current.name
                if enable:
                    e = "enabled"
                else:
                    e = "disabled"
                log(f"        #{o} {name} at {offset} '{select}' {e}", level=1, prefix=self)
                o += 1

        EngineClock.singleton().register(self).resume(self)

    # Shift position by the given offset.
    def shift(self, offset):
        (ox, oy)      = offset
        (x, y)        = self.position
        self.position = (x + ox, y + oy)

    def animation(self, name, enable=True):
        self._animations[name]["enable"] = enable
        player = self._animations[name]["animation_player"]
        if enable:
            player.resume().show()
        else:
            player.pause().hide()

    def blit(self):
        (px, py) = self.position
        for name in self._animation_order:
            a = self._animations[name]
            if not a["enable"]:
                continue
            (ox, oy) = a["offset"]
            a["animation_player"].blit_at((px + ox, py + oy))

    def is_done(self):
        return False

    def add_time(self, _):
        self.blit()

def main(argv=[]):
    log(f"Current Working Directory: {getcwd()}", level=1, prefix="main")

    init()
    Screen.singleton()
    mouse_set_visible(True)

    Sprite("monolith-0", (400, 270))
    sprite_count = 1

    af     = AnimationFactory.singleton()
    clock  = EngineClock.singleton()
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
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    Sprite("monolith-0", mouse_pos())
                    sprite_count += 1

        screen.reset(WHITE)
        clock.tick()

        y = 30
        text("Engine Clock:",       (30, y))
        text("    FPS:",            (30, y+10)); text(f"{clock.fps()}",                (130, y+10))
        text("    Running Tasks:",  (30, y+20)); text(f"{clock.running_task_count()}", (130, y+20))
        text("    Paused Tasks:",   (30, y+30)); text(f"{clock.paused_task_count()}",  (130, y+30))
        text("Counters:",           (30, y+40))
        text("    Sprite:",         (30, y+50)); text(f"{sprite_count}",               (130, y+50))
        text("    Blit:",           (30, y+60)); text(f"{screen.blit_count}",          (130, y+60))
        text("    Animation Load:", (30, y+70)); text(f"{af.load_count}",              (130, y+70))

        text("Log Level:",         (30, y+100)); text(f"{log_level}",                 (130, y+100))

        text(f"Keys:",           (30, 530))
        text(f"    Q/ESC",       (30, 540)); text(f"Exit", (130, 540))

        flip()

    # NOTREACHED

if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv) )
