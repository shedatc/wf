from pygame         import BLEND_RGBA_ADD, Rect
from pygame.display import flip as display_flip
from pygame.draw    import rect as draw_rect
from pygame.event   import get as events_get
from pygame.key     import set_repeat

from pygame_menu        import Menu
from pygame_menu.events import BACK

from ..Config       import Config
from ..EngineConfig import EngineConfig
from ..Screen       import Screen
from ..utils        import log_ex

from .ButtonConf   import ButtonConf
from .CheckboxConf import CheckboxConf
from .MenuConf     import MenuConf
from .SelectorConf import SelectorConf

class MainMenu:

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
        (self.width, self.height) = Screen.singleton().size

        # Build the arena list
        config     = Config.singleton().load("engine.json")
        arena_list = []
        for arena in config["arena_list"]:
            arena_list.append((arena["label"], arena["name"]))

        # Build the game type list
        type_list = [("DUEL", EngineConfig.TYPE_SINGLE_DUEL),
                     ("2v2",  EngineConfig.TYPE_SINGLE_2V2)]

        game_menu_conf = (
            ButtonConf(  "START", action=self._play),
            SelectorConf("TYPE",  items=type_list,  id="type"),
            SelectorConf("ARENA", items=arena_list, id="arena"),
        )

        def update_fullscreen(_, enabled):
            config               = Config.singleton().load("screen.json")
            orig_value           = config["fullscreen"]
            config["fullscreen"] = enabled
            MainMenu.log(f"screen.fullscreen: {orig_value} → {enabled}")

        def save_screen_conf(menu, *args, **kwargs):
            config = Config.singleton()
            config.save("screen.json")
            menu.reset(1)

        graphics_menu_conf = [
            CheckboxConf("FULLSCREEN",
                         enable=Config.singleton().load("screen.json")["fullscreen"],
                         action=update_fullscreen)
        ]

        def create_update_func(log_category):
            def update(_, enabled):
                config                       = Config.singleton().load("engine.json")
                orig_value                   = config["logs"][log_category]
                config["logs"][log_category] = enabled
                MainMenu.log(f"logs.{log_category}: {orig_value} → {enabled}")
            return update

        logging_menu_conf = []
        for log_category, enable in Config.singleton().get_log_categories().items():
            logging_menu_conf.append(
                CheckboxConf(log_category.upper(),
                             enable=enable,
                             id=f"logging_{log_category}",
                             action=create_update_func(log_category)) )

        def save_logging_conf(menu, *args, **kwargs):
            Config.singleton().save("engine.json")
            menu.reset(1)

        options_menu_conf = (
            MenuConf("GRAPHICS", conf=graphics_menu_conf,
                     back_action=save_screen_conf),
            MenuConf("LOGGING", conf=logging_menu_conf,
                     back_action=save_logging_conf),
        )

        main_menu_conf = (
            MenuConf(  "SINGLE PLAYER", conf=game_menu_conf),
            ButtonConf("MULTIPLAYER"),
            MenuConf(  "OPTIONS",       conf=options_menu_conf),
            ButtonConf("CREDITS"),
            ButtonConf("EXIT",          action=self._exit),
        )
        main_menu = Menu("", self.width, self.height, theme=MenuConf.create_theme())
        for conf in main_menu_conf:
            conf.add(main_menu)

        self._current = main_menu

    def _get(self, id):
        (item,  _) = self._current.get_input_data(recursive=True)[id]
        (_, value) = item
        return value

    def _dump(self):
        MainMenu.log( "Engine Config:")
        MainMenu.log(f"    Action: {self.engine_config.action}")
        MainMenu.log(f"    Arena:  {self.engine_config.arena}")
        MainMenu.log(f"    Type:   {self.engine_config.type}")

    def _play(self, **kwargs):
        MainMenu.log("PLAY")
        self.engine_config.action = EngineConfig.ACTION_PLAY
        self.engine_config.arena  = self._get("arena")
        self.engine_config.type   = self._get("type")
        self._current.disable()

    def _exit(self):
        MainMenu.log("EXIT")
        self.engine_config.action = EngineConfig.ACTION_EXIT
        self._current.disable()

    def _draw_highlight(self, surface):
        (screen_width, screen_height) = Screen.singleton().size
        (w, h)                        = (400, 40)
        (wo, ho)                      = (0, 17)
        draw_rect(surface, (200, 0, 0),
                  Rect(((screen_width - w) // 2 + wo, (screen_height - h) // 2 + ho), (w, h)))

    def _draw_background(self, surface):
        (screen_width, screen_height) = Screen.singleton().size
        surface.fill((0, 0, 100, 128),
                     rect=Rect((0, 0), (screen_width, screen_height // 2 - 20)),
                     special_flags=BLEND_RGBA_ADD)

    def run(self):
        set_repeat() # Disable keyboard repeat.
        self.engine_config = EngineConfig()
        surface            = Screen.singleton().surface
        self._current.enable()
        while True:
            surface.fill((0, 0, 0))

            self._draw_highlight(surface)

            if self._current.is_enabled():
                self._current.update( events_get() )
                if not self._current.is_enabled():
                    break
                self._current.draw(surface)

            self._draw_background(surface)

            display_flip()

        self._dump()
        return self.engine_config
