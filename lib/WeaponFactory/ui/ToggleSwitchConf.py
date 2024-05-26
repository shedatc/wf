from ..colors import COLOR_TRANSPARENT

from .WidgetConf import WidgetConf

class ToggleSwitchConf(WidgetConf):

    def __init__(self, label, enable=False):
        WidgetConf.__init__(self, label)
        self.enable = enable

    def add(self, menu):
        kwargs = {
            "float":               True,
            "state_color":         (COLOR_TRANSPARENT,  # Off
                                    COLOR_TRANSPARENT), # On
            "slider_color":        COLOR_TRANSPARENT,
            "switch_border_color": COLOR_TRANSPARENT,
        }
        menu.add.toggle_switch(self.label, self.enable, **kwargs)
