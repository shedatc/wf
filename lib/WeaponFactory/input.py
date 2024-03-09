import json
import os
import os.path
import pygame

from pygame import Rect

from .utils import Config, log_ex

# A key is a keyboard key. Its name starts with KEY_, e.g., KEY_F1.
#
# A button is a mouse button. Its name starts with MOUSE_, e.g.,
# MOUSE_BUTTON_LEFT.
class InputHandler:

    MOUSE_BUTTONS = ["BUTTON_LEFT", "BUTTON_MIDDLE", "BUTTON_RIGHT"]

    def log(msg):
        log_ex(msg, category="InputHandler")

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

    def blit(self, surface):
        (width, height)               = (10, 13)
        (screen_width, screen_height) = pygame.display.get_surface().get_size()
        (x, y)                        = (screen_width - width, screen_height - height)
        pygame.draw.rect(surface, self.background_color, Rect((x, y), (width, height)))
        pygame.draw.rect(surface, self.foreground_color, Rect((x, y), (width, height)),
                         width=1)
        font      = pygame.font.Font(None, 15)
        text_surf = font.render(self.abbrev,
                                False,                 # Antialias
                                self.foreground_color)
        surface.blit(text_surf, (x + 2, y + 2))

class ModalInputHandler:

    def log(msg):
        log_ex(msg, category="ModalInputHandler")

    def __init__(self):
        self.inputHandlers       = {}
        self.funcs               = {}
        self.currentInputHandler = None
        self.currentMode         = None

    def addMode(self, mode):
        ModalInputHandler.log(f"+mode: {mode}")
        ih = InputHandler()
        for name, func in self.funcs.items():
            ih.addFunc(name, func)
        self.inputHandlers[mode] = ih
        return ih

    def enterMode(self, mode):
        self.currentInputHandler = self.inputHandlers[mode]
        self.currentMode   = mode
        ModalInputHandler.log(f"enter mode: {mode}")

    def addFunc(self, name, func):
        ModalInputHandler.log(f"+func: {name}")
        self.funcs[name] = func
        for mode, inputHandler in self.inputHandlers.items():
            inputHandler.addFunc(name, func)

    def configure(self):
        config      = Config.singleton().load("input.json")
        defaultMode = config["default-mode"]
        if "repeat" in config:
            delay    = config["repeat"]["delay"]
            interval = config["repeat"]["interval"]
            ModalInputHandler.log(f"repeat: delay={delay} interval={interval}")
            pygame.key.set_repeat(delay, interval)
        for mode, config in config["modes"].items():
           self.addMode(mode).configure(config)
        self.enterMode(defaultMode)

    def probe(self):
        self.currentInputHandler.probe()

    def blit(self, surface):
        self.currentInputHandler.blit(surface)

class Mouse:

    def get_coords():
        return pygame.mouse.get_pos()
