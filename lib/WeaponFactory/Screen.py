from math           import radians
from pygame         import DOUBLEBUF, FULLSCREEN, OPENGL, Rect, SCALED
from pygame.display import get_desktop_sizes, get_driver, get_wm_info, Info, list_modes
from pygame.display import set_caption, set_mode
from pygame.draw    import arc  as draw_arc
from pygame.draw    import line as draw_line
from pygame.draw    import rect as draw_rect
from pygame.font    import Font
from pygame.math    import Vector2

from .Camera      import Camera
from .Config      import Config
from .StatCounter import StatCounter
from .colors      import COLOR_BLACK, COLOR_GREEN
from .debug       import DEBUG_BLIT
from .utils       import must_log, log_ex, sz

class Screen:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        config = Config.singleton().load("screen.json")
        size   = (config["width"], config["height"])
        if "caption" in config:
            caption = config["caption"]
        else:
            caption = None

        flags     = 0
        flags_str = []
        if "doublebuf" in config and config["doublebuf"] is True:
            flags |= DOUBLEBUF
            flags_str.append("DOUBLEBUF")
        if "fullscreen" in config and config["fullscreen"] is True:
            flags |= FULLSCREEN
            flags_str.append("FULLSCREEN")
        if "opengl" in config and config["opengl"] is True:
            flags |= OPENGL
            flags_str.append("OPENGL")
        if "scaled" in config and config["scaled"] is True:
            flags |= SCALED
            flags_str.append("SCALED")

        Screen.log(f"Screen:")
        Screen.log(f"    Flags:   {', '.join(flags_str)}")
        Screen.log(f"    Size:    {sz(size)}")
        Screen.log(f"    Caption: {caption}")
        Screen.log(f"    Available Modes:")
        for w, h in list_modes():
            Screen.log(f"        {w}x{h}")
        Screen.log(f"    Available Desktop Sizes:")
        for w, h in get_desktop_sizes():
            Screen.log(f"        {w}x{h}")

        self.surface = set_mode(size, flags, depth=8)
        rect         = self.surface.get_rect()
        self.size    = rect.size
        if caption is not None:
            set_caption(caption)
        self._font = Font(None, 15)

        i = Info()
        Screen.log(f"Display:")
        Screen.log(f"    Backend:               {get_driver()}")
        Screen.log(f"    Size:                  {i.current_w}x{i.current_h}")
        Screen.log(f"    Hardware Acceleration: {i.hw}")
        Screen.log(f"    Windowed:              {i.wm}")
        if i.video_mem == 0:
            video_mem_str = "Unknown"
        else:
            video_mem_str = "{i.video_mem}MB"
        Screen.log(f"    Video Memory:          {video_mem_str}")
        Screen.log(f"    Bit Size:              {i.bitsize} bits/pixel")
        Screen.log(f"    Byte Size:             {i.bytesize} bytes/pixel")
        Screen.log(f"    Masks:                 {i.masks}")
        Screen.log(f"    Shifts:                {i.shifts}")
        Screen.log(f"    Losses:                {i.losses}")
        Screen.log(f"    Hardware Surface Acceleration:")
        Screen.log(f"        Blitting:             {i.blit_hw}")
        Screen.log(f"        Colorkey Blitting:    {i.blit_hw_CC}")
        Screen.log(f"        Pixel alpha Blitting: {i.blit_hw_A}")
        Screen.log(f"    Software Surface Acceleration:")
        Screen.log(f"        Blitting:             {i.blit_sw}")
        Screen.log(f"        Colorkey Blitting:    {i.blit_sw_CC}")
        Screen.log(f"        Pixel alpha Blitting: {i.blit_sw_A}")

        if must_log(Screen.__name__):
            # FIXME Calling the following code while screen logging is disabled
            # trigger a SIGSEGV:
            # #0  0x00007e260f94dab0 in PyDict_SetItem () from /usr/lib/libpython3.13.so.1.0
            # #1  0x00007e260f9537df in PyDict_SetItemString () from /usr/lib/libpython3.13.so.1.0
            # #2  0x00007e260f4f0c95 in ?? () from /usr/lib/python3.13/site-packages/pygame/display.cpython-313-x86_64-linux-gnu.so
            # #3  0x00007e260f96022b in ?? () from /usr/lib/libpython3.13.so.1.0
            # #4  0x00007e260f95f82d in PyObject_Vectorcall () from /usr/lib/libpython3.13.so.1.0
            # #5  0x00007e260f96ecd4 in _PyEval_EvalFrameDefault () from /usr/lib/libpython3.13.so.1.0
            # #6  0x00007e260f9a5958 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #7  0x00007e260f95d3bc in _PyObject_MakeTpCall () from /usr/lib/libpython3.13.so.1.0
            # #8  0x00007e260f96ecd4 in _PyEval_EvalFrameDefault () from /usr/lib/libpython3.13.so.1.0
            # #9  0x00007e260f9a5958 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #10 0x00007e260f95d3bc in _PyObject_MakeTpCall () from /usr/lib/libpython3.13.so.1.0
            # #11 0x00007e260f96ecd4 in _PyEval_EvalFrameDefault () from /usr/lib/libpython3.13.so.1.0
            # #12 0x00007e260f9a5a40 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #13 0x00007e260f95d3bc in _PyObject_MakeTpCall () from /usr/lib/libpython3.13.so.1.0
            # #14 0x00007e260f978788 in _PyEval_EvalFrameDefault () from /usr/lib/libpython3.13.so.1.0
            # #15 0x00007e260fa41695 in PyEval_EvalCode () from /usr/lib/libpython3.13.so.1.0
            # #16 0x00007e260fa7f433 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #17 0x00007e260fa7c81a in ?? () from /usr/lib/libpython3.13.so.1.0
            # #18 0x00007e260fa79f27 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #19 0x00007e260fa791e0 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #20 0x00007e260fa78ff3 in ?? () from /usr/lib/libpython3.13.so.1.0
            # #21 0x00007e260fa77244 in Py_RunMain () from /usr/lib/libpython3.13.so.1.0
            # #22 0x00007e260fa2e95c in Py_BytesMain () from /usr/lib/libpython3.13.so.1.0
            # #23 0x00007e260f6376b5 in ?? () from /usr/lib/libc.so.6
            # #24 0x00007e260f637769 in __libc_start_main () from /usr/lib/libc.so.6
            # #25 0x0000570e3387f045 in _start ()

            i = get_wm_info()
            Screen.log(f"Windowing System:")
            for k, v in i.items():
                Screen.log(f"        {k}: {v}")

        self.blit_count = StatCounter()

    def reset(self):
        Screen.log(f"Reset")
        self.blit_count.reset()
        self.surface.fill(COLOR_BLACK)

    def _blit_needed(self, source_surface, screen_point, source_rect=None):
        if source_rect is None:
            source_rect = source_surface.get_rect()
        screen_rect       = self.surface.get_rect()
        dest_rect         = Rect(screen_point, source_rect.size)
        clipped_dest_rect = screen_rect.clip(dest_rect)
        return clipped_dest_rect

    def screen_blit(self, source_surface, screen_point, source_rect=None):
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit {source_surface} to screen at {screen_point}")
            else:
                Screen.log(f"Blit {source_rect} from {source_surface} to screen at {screen_point}")

        if not self._blit_needed(source_surface, screen_point, source_rect=source_rect):
            return
        self.surface.blit(source_surface, screen_point, area=source_rect)
        self.blit_count += 1

    def blit(self, source_surface, world_point, source_rect=None):
        screen_point = Camera.singleton().screen_point(world_point)
        if DEBUG_BLIT:
            if source_rect is None:
                Screen.log(f"Blit {source_surface} to screen" \
                           + f" at {world_point} → {screen_point}")
            else:
                Screen.log(f"Blit {source_rect} from {source_surface} to screen" \
                           + f" at {world_point} → {screen_point}")
        if not self._blit_needed(source_surface, screen_point, source_rect=source_rect):
            return
        self.surface.blit(source_surface, screen_point, area=source_rect)
        self.blit_count += 1

    def screen_draw_rect(self, screen_rect, color=COLOR_BLACK, width=0):
        draw_rect(self.surface, color, screen_rect, width=width)

    # FIXME Should avoid drawing things that are out of the screen surface.
    def draw_rect(self, world_rect, color=COLOR_BLACK, width=0):
        screen_rect        = world_rect.copy()
        screen_rect.center = Camera.singleton().screen_point(world_rect.center),
        draw_rect(self.surface, color, screen_rect, width=width)

    def screen_text(self, text, screen_point,
                    color=COLOR_GREEN, bgcolor=COLOR_BLACK):
        text_surf = self._font.render(text,
                                      True,            # antialias
                                      color,
                                      bgcolor)
        self.screen_blit(text_surf, screen_point)

    def text(self, text, world_point,
             color=COLOR_GREEN, bgcolor=COLOR_BLACK):
        screen_point = Camera.singleton().screen_point(world_point),
        self.screen_text(text, screen_point, color=color, bgcolor=bgcolor)

    def draw_point(self, world_point, name=None, color=COLOR_BLACK, stats=False, width=1):
        rect = Rect((0, 0), (width, width))
        rect.center = world_point
        self.draw_rect(rect, color=color, width=width)
        (tx, ty) = rect.bottomright
        tx += 10
        if name is None:
            return
        if stats:
            self.text(f"{name}: {world_point}", (tx, ty), color=color)
        else:
            self.text(f"{name}", (tx, ty), color=color)

    def draw_line(self, world_start, world_end,
                  color=COLOR_BLACK, width=1):
        camera       = Camera.singleton()
        screen_start = camera.screen_point(world_start)
        screen_end   = camera.screen_point(world_end)
        draw_line(self.surface, color, screen_start, screen_end, width)

    def draw_vector(self, world_point, vector,
                    name=None, color=COLOR_BLACK, width=1, stats=False):
        if type(world_point) is Vector2:
            (px, py) = world_point.xy
        else:
            (px, py) = world_point
        if type(vector) is Vector2:
            (vx, vy) = vector.xy
        else:
            (vx, vy) = vector
        self.draw_line(world_point, (px + vx, py + vy), color=color, width=width)
        rect = Rect((0, 0), (5, 5))
        rect.center = (px + vx, py + vy)
        self.draw_rect(rect, color=color)
        if name is None:
            return
        (tx, ty) = rect.bottomright
        tx += 10
        if stats:
            self.text(f"{name}: {vector.xy}",             (tx, ty),      color=color)
            self.text(f"     len: {vector.length():.2f}", (tx, ty + 10), color=color)
        else:
            self.text(name, (tx, ty), color=color)

    def draw_arc(self, rect, start_angle, stop_angle, color=COLOR_BLACK, width=1):
        screen_rect = Camera.singleton().screen_rect(rect)
        draw_arc(self.surface, color, screen_rect, radians(start_angle), radians(stop_angle),
                 width)
