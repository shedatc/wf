import pygame.draw
import pygame.event
import pygame.font
import pygame.key

from pygame import Rect

from .Screen import Screen
from .utils  import log_ex

# A key is a keyboard key. Its name starts with KEY_, e.g., KEY_F1.
#
# A button is a mouse button. Its name starts with MOUSE_, e.g.,
# MOUSE_BUTTON_LEFT.
class InputHandler:

    MOUSE_BUTTONS = ["BUTTON_LEFT", "BUTTON_MIDDLE", "BUTTON_RIGHT"]

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        self.key_pressed     = {}
        self.key_released    = {}
        self.button_pressed  = [None for i in InputHandler.MOUSE_BUTTONS]
        self.button_released = [None for i in InputHandler.MOUSE_BUTTONS]
        self.funcs           = {}
        self.abbrev          = None

    def addFunc(self, name, func):
        self.funcs[name] = func

    def _key_code2name(self, key_code):
        return "KEY_" + pygame.key.name(key_code).upper()

    def _key_name2code(self, key_name):
        assert key_name.startswith("KEY_")
        return pygame.key.key_code( key_name[len("KEY_"):].upper() )

    def _button_code2name(self, button_code):
        if button_code in InputHandler.MOUSE_BUTTONS:
            return "MOUSE_" + InputHandler.MOUSE_BUTTONS[button_code]
        else:
            return f"MOUSE_<{button_code}>"

    def _button_name2code(self, button_name):
        assert button_name.startswith("MOUSE_")
        return InputHandler.MOUSE_BUTTONS.index( button_name[len("MOUSE_"):].upper() )

    # key_name must starts with KEY_ or MOUSE_.
    def bind(self, key_or_button_name, func_name, released=False):
        func = self.funcs[func_name]
        if key_or_button_name.startswith("KEY_"):
            key_code = self._key_name2code(key_or_button_name)
            if released:
                self.key_released[key_code] = func
            else:
                self.key_pressed[key_code] = func
        elif key_or_button_name.startswith("MOUSE_"):
            button_code = self._button_name2code(key_or_button_name)
            if released:
                self.button_released[button_code] = func
            else:
                self.button_pressed[button_code] = func
        else:
            raise AssertionError("key_or_button_name must starts with KEY_ or MOUSE_")

    def configure(self, config):
        InputHandler.log(f"| {'Key'.ljust(20)} | {'Func'.ljust(40)} | {'Released'.ljust(8)} |")
        InputHandler.log(f"|-{'-' * 20}-+-{'-' * 40}-+-{'-' * 8}-|")
        if "pressed" in config["keys"].keys():
            for kbn, func_name in config["keys"]["pressed"].items():
                self.bind(kbn, func_name, False)
                InputHandler.log(f"| {kbn.rjust(20)} | {func_name.ljust(40)} | {'False'.rjust(8)} |")
        InputHandler.log(f"|-{'-' * 20}-+-{'-' * 40}-+-{'-' * 8}-|")
        if "released" in config["keys"].keys():
            for kbn, func_name in config["keys"]["released"].items():
                self.bind(kbn, func_name, True)
                InputHandler.log(f"| {kbn.rjust(20)} | {func_name.ljust(40)} | {'True'.rjust(8)} |")

        self.abbrev = config["abbrev"]
        InputHandler.log(f"Abbrev: {self.abbrev}")
        assert self.abbrev is not None
        assert len(self.abbrev) == 1

        self.foreground_color = tuple(config["colors"]["foreground"])
        self.background_color = tuple(config["colors"]["background"])
        InputHandler.log(f"Foreground Color: {self.foreground_color}")
        InputHandler.log(f"Background Color: {self.background_color}")

    def _trigger(self, desc, code, seq, code2name):
        name = code2name(code)
        try:
            func = seq[code]
        except (IndexError, KeyError):
            return
        else:
            InputHandler.log(f"{desc}: {code}<{name}> ⇒ {func}")
            if func is not None:
                func()

    def probe(self):
        # Keyboard keys:
        for event in pygame.event.get(pygame.KEYDOWN):
            self._trigger("Key pressed",
                          event.key, self.key_pressed, self._key_code2name)
        for event in pygame.event.get(pygame.KEYUP):
            self._trigger("Key released",
                          event.key, self.key_released, self._key_code2name)

        # Mouse buttons:
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            self._trigger("Button pressed",
                          event.button - 1, self.button_pressed, self._button_code2name)
        for event in pygame.event.get(pygame.MOUSEBUTTONUP):
            self._trigger("Button released",
                          event.button - 1, self.button_released, self._button_code2name)

    def blit(self):
        screen                        = Screen.singleton()
        (width, height)               = (10, 13)
        (screen_width, screen_height) = screen.size
        (x, y)                        = (screen_width - width, screen_height - height)
        rect                          = Rect((x, y), (width, height))
        screen.screen_draw_rect(rect, color=self.background_color)
        screen.screen_draw_rect(rect, color=self.foreground_color, width=1)
        font         = pygame.font.Font(None, 15)
        text_surface = font.render(self.abbrev,
                                   False,                 # Antialias
                                   self.foreground_color)
        screen.screen_blit(text_surface, (x + 2, y + 2))
