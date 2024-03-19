from pygame.key import set_repeat

from .InputHandler import InputHandler
from .utils        import Config, log_ex

class ModalInputHandler:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

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
        for _, inputHandler in self.inputHandlers.items():
            inputHandler.addFunc(name, func)

    def configure(self):
        config      = Config.singleton().load("input.json")
        defaultMode = config["default-mode"]
        if "repeat" in config:
            delay    = config["repeat"]["delay"]
            interval = config["repeat"]["interval"]
            ModalInputHandler.log(f"repeat: delay={delay} interval={interval}")
            set_repeat(delay, interval)
        for mode, config in config["modes"].items():
           self.addMode(mode).configure(config)
        self.enterMode(defaultMode)

    def probe(self):
        assert self.currentInputHandler is not None
        self.currentInputHandler.probe()

    def blit(self):
        assert self.currentInputHandler is not None
        self.currentInputHandler.blit()
