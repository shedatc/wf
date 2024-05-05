import pygame
from pygame      import Rect
from pygame.draw import rect as draw_rect

import pygame_menu
import pygame_menu.font
import pygame_menu.themes
import pygame_menu.widgets

from pygame_menu.events import BACK, EXIT

TRANSPARENT = (0, 0, 0, 0)

logo = None

class WidgetConf:

    def __init__(self, label):
        self.label = label

    def draw_widget(self, widget, menu):
        widgets = menu.get_widgets()

        selected = 0
        for i, widget in enumerate( widgets ):
            if widget.is_selected():
                selected = i

        def get_height_sum(w):
            h = 0
            for i, widget in enumerate( widgets ):
                if i == w:
                    break
                h += widget.get_height() + 2
            return h

        for i, widget in enumerate( widgets ):
            if i < selected:
                y = -get_height_sum(selected - i)
            else:
                y = get_height_sum(i - selected)
            widget.translate(0, y)

    def add(self, menu):
        raise NotImplementedError()

class ButtonConf(WidgetConf):

    def __init__(self, label, action=None):
        WidgetConf.__init__(self, label)
        self.action = action

    def add(self, menu):
        kwargs = {
            "float": True,
        }
        if self.action is None:
            b = menu.add.button(self.label, **kwargs)
        else:
            b = menu.add.button(self.label, self.action, menu, **kwargs)
        b.add_draw_callback(self.draw_widget)

class SelectorConf(WidgetConf):

    def __init__(self, label, items, selected=0):
        WidgetConf.__init__(self, label)
        self.items    = items
        self.selected = selected

    def add(self, menu):
        kwargs = {
            "float":   True,
            "items":   self.items,
            "default": self.selected,
        }
        b = menu.add.selector(self.label + " ", **kwargs)
        b.add_draw_callback(self.draw_widget)

class CheckboxConf(SelectorConf):

    def __init__(self, label, enable=False):
        if enable:
            selected = 0
        else:
            selected = 1
        SelectorConf.__init__(self, label, [("On", True), ("Off", False)], selected=selected)

class MenuConf(WidgetConf):

    @classmethod
    def create_theme(cls):
        if False:
            sdl_ttf_version = pygame.font.get_sdl_ttf_version()
            sdl_ttf_version = ".".join( map(str, sdl_ttf_version) )
            print(f"SDL TTL Version: {sdl_ttf_version}")
            print(f"Fonts:")
            for font in pygame.font.get_fonts():
                print(f"    {font}")
        # font_path = pygame.font.match_font("freemono")
        fonts = [
            "/home/sheda/t/fonts/EightBitDragon-anqx.ttf",            # OK
            "/home/sheda/t/fonts/8bit_wonder/8-BIT WONDER.TTF",       # MISSING CHARACTERS: <, >, :
            "/home/sheda/t/fonts/8Bit-44Pl.ttf",                      # OK
            "/home/sheda/t/fonts/PoppkornRegular-MzKY.ttf",           # DIFFICULT TO READ
            "/home/sheda/t/fonts/EndlessBossBattleRegular-v7Ey.ttf",  # OK
            "/home/sheda/t/fonts/8-bit Arcade Out.ttf",               # MISSING CHARACTERS: <, >, :
            "/home/sheda/t/fonts/8-bit Arcade In.ttf",                # MISSING CHARACTERS: <, >, :
            "/home/sheda/t/fonts/ka1.ttf",                            # MISSING CHARACTERS: <, >, :
            "/home/sheda/t/fonts/8_bit_hud/8-bit-hud.ttf",            # OK, 8-bit HUD by Seba Perez
        ]
        font_path = fonts[8]
        font = pygame.font.Font(font_path, 20)
        print(f"Font: {font_path}")

        theme                         = pygame_menu.themes.THEME_DEFAULT.copy()
        theme.title_font              = font
        theme.widget_font             = font
        theme.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
        theme.title_bar_style         = pygame_menu.widgets.MENUBAR_STYLE_NONE
        theme.background_color        = TRANSPARENT
        return theme

    def __init__(self, label, conf):
        WidgetConf.__init__(self, label)
        self.conf = conf

    def add(self, menu):
        submenu = pygame_menu.Menu("", 800, 600,
                                   theme=MenuConf.create_theme(),
                                   overflow=True)
        for conf in self.conf:
            conf.add(submenu)

        kwargs = {
            "float": True,
        }
        submenu.add.button("BACK", BACK, **kwargs) \
                   .add_draw_callback(self.draw_widget)

        menu.add.button(self.label, submenu, **kwargs) \
                .add_draw_callback(self.draw_widget)

class ToggleSwitchConf(WidgetConf):

    def __init__(self, label, enable=False):
        WidgetConf.__init__(self, label)
        self.enable = enable

    def add(self, menu):
        kwargs = {
            "float": True,
            "state_color": (TRANSPARENT,  # Off
                            TRANSPARENT), # On
            "slider_color": TRANSPARENT,
            "switch_border_color": TRANSPARENT,
        }
        menu.add.toggle_switch(self.label, self.enable, **kwargs)

class DropSelectMultipleConf(WidgetConf):

    def __init__(self, label, items):
        WidgetConf.__init__(self, label)
        self.items = items

    def add(self, menu):
        kwargs = {
            "float": True,
            "items": self.items,
        }
        menu.add.dropselect_multiple(self.label, **kwargs)

def draw_background(surface):
    rect = Rect((100, -50), (600, 297))
    surface.fill((0, 0, 200, 128), rect, pygame.BLEND_RGBA_ADD)
    return

def main(argv=[]):
    pygame.init()
    (screen_width, screen_height) = (800, 600)
    surface = pygame.display.set_mode((screen_width, screen_height))

    root_menu = pygame_menu.Menu("", 800, 600,
                                 theme=MenuConf.create_theme(),
                                 overflow=True)
    logging_menu_conf = (
        CheckboxConf("ANIMATION",        enable=True),
        CheckboxConf("ANIMATIONFACTORY", enable=False),
        CheckboxConf("ANIMATIONFRAME",   enable=False),
    )
    options_menu_conf = (
        MenuConf("LOGGING", conf=logging_menu_conf),
    )
    root_menu_conf = (
        ButtonConf("START"),
        ButtonConf("MULTIPLAYER"),
        SelectorConf("DIFFCULTY",             items=[("High", 2), ("Medium", 1), ("Low", 0)]),
        ToggleSwitchConf("TOGGLE SWITCH",     enable=True),
        DropSelectMultipleConf("DROP_SELECT", items=[("High", 2), ("Medium", 1), ("Low", 0)]),
        MenuConf("OPTIONS",                   conf=options_menu_conf),
        ButtonConf("CREDITS"),
        ButtonConf("EXIT",                    action=EXIT),
    )
    for conf in root_menu_conf:
        conf.add(root_menu)
    root_menu.enable()

    while True:

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                break

        surface.fill((0, 0, 0))

        # Highlight selected entry
        w = 660
        rect = Rect(((screen_width - w) // 2, 297), (w, 40))
        draw_rect(surface, (200, 0, 0), rect)

        if root_menu.is_enabled():
            root_menu.update(events)
            if not root_menu.is_enabled():
                break
            root_menu.draw(surface)
        draw_background(surface)

        pygame.display.update()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit( main(sys.argv) )
