from pygame.font import Font, get_fonts, get_sdl_ttf_version

from pygame_menu         import Menu
from pygame_menu.events  import BACK
from pygame_menu.themes  import THEME_DEFAULT
from pygame_menu.widgets import MENUBAR_STYLE_NONE, SimpleSelection

from ..Assets import Assets
from ..Screen import Screen
from ..colors import COLOR_TRANSPARENT

from .WidgetConf import WidgetConf

class MenuConf(WidgetConf):

    @classmethod
    def create_theme(cls):
        theme                         = THEME_DEFAULT.copy()
        theme.background_color        = COLOR_TRANSPARENT
        theme.title_bar_style         = MENUBAR_STYLE_NONE
        theme.title_font              = Font(Assets.locate("font", "8-bit-hud.ttf"), 20)
        theme.widget_font             = theme.title_font
        theme.widget_selection_effect = SimpleSelection()
        return theme

    def __init__(self, label, conf, back_action=BACK, back_args=()):
        WidgetConf.__init__(self, label)
        self.back_action = back_action
        self.back_args   = back_args
        self.conf        = conf

    def _add_back_button(self, menu):
        kwargs = {
            "float": True,
        }
        back_args = (menu,) + self.back_args
        menu.add.button("BACK", self.back_action, *back_args, **kwargs) \
            .add_draw_callback(self.draw_widget)

    def add(self, menu):
        screen                        = Screen.singleton()
        (screen_width, screen_height) = screen.size
        submenu = Menu("", screen_width, screen_height,
                       theme=MenuConf.create_theme(),
                       overflow=True)
        for conf in self.conf:
            conf.add(submenu)
        self._add_back_button(submenu)

        kwargs = {
            "float": True,
        }
        menu.add.button(self.label, submenu, **kwargs) \
                .add_draw_callback(self.draw_widget)
