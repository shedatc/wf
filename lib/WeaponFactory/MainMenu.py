from pygame.key  import set_repeat
from pygame_menu import Menu

from .Config       import Config
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

        config      = Config.singleton().load("engine.json")
        arena_items = []
        for arena in config["arena_list"]:
            arena_items.append((arena["label"], arena["name"]))
        self.menu.add.selector("Arena:", arena_items, selector_id="arena",
                               onreturn=self.pick_arena)
        self.menu.add.button('Play', self.play)
        self.menu.add.button('Exit', self.exit)

    def get(self, id):
        (item,  _) = self.menu.get_input_data()[id]
        (_, value) = item
        return value

    def dump(self):
        MainMenu.log(f"Engine Config:")
        MainMenu.log(f"    Arena: {self.engine_config.arena}")

    def pick_arena(self, item, index):
        self.play()

    def play(self, foo=None, bar=None):
        MainMenu.log(f"PLAY")
        self.engine_config.action = START_GAME
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
        self.engine_config.arena = self.get("arena")
        self.dump()
        return self.engine_config
