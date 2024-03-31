from pygame.key  import set_repeat
from pygame_menu import Menu

from .EngineConfig import EngineConfig, EXIT_ENGINE, START_GAME
from .Screen       import Screen
from .utils        import log_ex

class MainMenu:

    _singleton = None

    @classmethod
    def singleton(cls):
        assert cls._singleton is not None
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        screen                        = Screen.singleton()
        (screen_width, screen_height) = screen.size
        self.menu                     = Menu('Weapon Factory', screen_width, screen_height)
        self.menu.add.button('Play', self.play)
        self.menu.add.button('Exit', self.exit)

    def play(self):
        MainMenu.log(f"PLAY")
        self.engine_config.action = START_GAME
        self.engine_config.arena  = "arena-1"
        self.menu.disable()

    def exit(self):
        MainMenu.log(f"EXIT")
        self.engine_config.action = EXIT_ENGINE
        self.menu.disable()

    def run(self):
        set_repeat() # Disable keyboard repeat.
        self.engine_config = EngineConfig()
        self.menu.enable()
        self.menu.mainloop(Screen.singleton().surface)
        return self.engine_config
