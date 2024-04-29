from pygame         import BLEND_RGBA_ADD, Rect
from pygame.display import flip as display_flip
from pygame.draw    import rect as draw_rect
from pygame.event   import get as events_get
from pygame.font    import Font
from pygame.key     import set_repeat

from pygame_menu                          import Menu
from pygame_menu.themes                   import THEME_DEFAULT
from pygame_menu.widgets.selection.simple import SimpleSelection
from pygame_menu.widgets.widget.menubar   import MENUBAR_STYLE_NONE

from .Assets       import Assets
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

    def _build_theme(self):
        theme                         = THEME_DEFAULT.copy()
        theme.background_color        = (0, 0, 0, 0) # Transparent
        theme.title_bar_style         = MENUBAR_STYLE_NONE
        theme.title_font              = Font(Assets.locate("font", "8-bit-hud.ttf"), 20)
        theme.widget_font             = theme.title_font
        theme.widget_selection_effect = SimpleSelection()
        return theme

    def _draw_widget(self, widget, menu):
        selected = 0
        for i, widget in enumerate( menu.get_widgets() ):
            if widget.is_selected():
                selected = i
        for i, widget in enumerate( menu.get_widgets() ):
            y = ( i - selected) * 42
            widget.translate(0, y)

    def _add_button(self, label, **kwargs):
        required_kwargs = {
            "float": True,
        }
        for k, v in required_kwargs.items():
            kwargs[k] = v
        w = self.menu.add.button(label, **kwargs)
        w.add_draw_callback(self._draw_widget)
        return w

    def _add_selector(self, label, items, **kwargs):
        required_kwargs = {
            "float": True,
        }
        for k, v in required_kwargs.items():
            kwargs[k] = v
        w = self.menu.add.selector(label, items, **kwargs)
        w.add_draw_callback(self._draw_widget)
        return w

    def __init__(self):
        (screen_width, screen_height) = Screen.singleton().size

        self.menu = Menu("",
                         screen_width, screen_height,
                         theme=self._build_theme())

        config = Config.singleton().load("engine.json")
        self._add_button("START", action=self._play)
        arena_items = []
        for arena in config["arena_list"]:
            arena_items.append((arena["label"], arena["name"]))
        self._add_selector("ARENA ", arena_items, selector_id="arena",
                           onreturn=self._pick_arena)
        self._add_button("MULTIPLAYER")
        self._add_button("OPTIONS")
        self._add_button("CREDITS")
        self._add_button("EXIT", action=self._exit)

    def _get(self, id):
        (item,  _) = self.menu.get_input_data()[id]
        (_, value) = item
        return value

    def _dump(self):
        MainMenu.log(f"Engine Config:")
        MainMenu.log(f"    Arena: {self.engine_config.arena}")

    def _pick_arena(self, item, index):
        self._play()

    def _play(self, **kwargs):
        MainMenu.log(f"PLAY")
        self.engine_config.action = START_GAME
        self.menu.disable()

    def _exit(self):
        MainMenu.log(f"EXIT")
        self.engine_config.action = EXIT_ENGINE
        self.menu.disable()

    def _draw_background(self, surface):
        screen                        = Screen.singleton()
        (screen_width, screen_height) = screen.size
        surface.fill((0, 0, 100, 128),
                     rect=Rect((0, 0), (screen_width, screen_height // 2 - 20)),
                     special_flags=BLEND_RGBA_ADD)

    def run(self):
        set_repeat() # Disable keyboard repeat.
        self.engine_config = EngineConfig()
        self.menu.enable()
        surface = Screen.singleton().surface
        while True:
            surface.fill((0, 0, 0))

            rect = Rect((70, 190), (400, 40))
            draw_rect(surface, (200, 0, 0), rect)

            self.menu.update( events_get() )
            if not self.menu.is_enabled():
                break
            self.menu.draw(surface)

            self._draw_background(surface)

            display_flip()

        self.engine_config.arena = self._get("arena")
        self._dump()
        return self.engine_config
