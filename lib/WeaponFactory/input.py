import json
import os
import os.path
import pyxel

from .const import SCREEN_WIDTH, SCREEN_HEIGHT
from .utils import Config, logEx

class InputHandler:

    def log(msg):
        logEx(msg, category="InputHandler")

    def __init__(self):
        self.pressed  = {}
        self.released = {}
        self.funcs    = {}
        self.abbrev   = None

    def addFunc(self, name, func):
        self.funcs[name] = func

    def bindKey(self, key, name, released=False):
        if released:
            self.released[key] = self.funcs[name]
        else:
            self.pressed[key] = self.funcs[name]

    def string2key(self, string):
        string = string.upper()
        key    = pyxel.__dict__.get(string.upper())
        assert key is not None, f"unknown key {string}"
        return key

    def key2string(self, key):
        for k, v in pyxel.__dict__.items():
            if v == key:
                return k
        else:
            return None

    def configure(self, config):
        InputHandler.log(f"| {'Key'.ljust(20)} | {'Func'.ljust(40)} | {'Released'.ljust(8)} |")
        InputHandler.log(f"|-{'-' * 20}-+-{'-' * 40}-+-{'-' * 8}-|")
        if "pressed" in config["keys"].keys():
            for k, func in config["keys"]["pressed"].items():
                key = self.string2key(k)
                self.bindKey(key, func, False)
                InputHandler.log(f"| {k.upper().rjust(20)} | {func.ljust(40)} | {'False'.rjust(8)} |")
        InputHandler.log(f"|-{'-' * 20}-+-{'-' * 40}-+-{'-' * 8}-|")
        if "released" in config["keys"].keys():
            for k, func in config["keys"]["released"].items():
                key = self.string2key(k)
                self.bindKey(key, func, True)
                InputHandler.log(f"| {k.upper().rjust(20)} | {func.ljust(40)} | {'True'.rjust(8)} |")

        self.abbrev = config["abbrev"]
        InputHandler.log(f"Abbrev: {self.abbrev}")
        assert self.abbrev is not None
        assert len(self.abbrev) == 1

        self.foregroundColor = config["colors"]["foreground"]
        self.backgroundColor = config["colors"]["background"]

    def probeKeys(self):
        for key, func in self.pressed.items():
            if pyxel.btn(key):
                InputHandler.log(f"Key pressed: {key}<{self.key2string(key)}>")
                func()
        for key, func in self.released.items():
            if pyxel.btnr(key):
                InputHandler.log(f"Key released: {key}<{self.key2string(key)}>")
                func()

    def draw(self):
        (width, height) = (7, 9)
        (x, y)          = (pyxel.width - width, pyxel.height - height)
        pyxel.rect(x, y, width, height, self.backgroundColor)
        pyxel.rectb(x, y, width, height, self.foregroundColor)
        pyxel.text(x + 2, y + 2, self.abbrev, self.foregroundColor)

class ModalInputHandler:

    def log(msg):
        logEx(msg, category="ModalInputHandler")

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
        config      = Config.load("input.json")
        defaultMode = config["default-mode"]
        for mode, config in config["modes"].items():
           self.addMode(mode).configure(config)
        self.enterMode(defaultMode)

    def probe(self):
        self.currentInputHandler.probeKeys()

    def draw(self):
        self.currentInputHandler.draw()

class Mouse:

    def getCoords():
        mx = max(0, min(pyxel.mouse_x, SCREEN_WIDTH - 1))
        my = max(0, min(pyxel.mouse_y, SCREEN_HEIGHT - 1))
        return (mx, my)
