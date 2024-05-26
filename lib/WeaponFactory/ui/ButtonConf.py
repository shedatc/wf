from .WidgetConf import WidgetConf

class ButtonConf(WidgetConf):

    def __init__(self, label, action=None):
        WidgetConf.__init__(self, label)
        self.action = action

    def add(self, menu):
        kwargs = {
            "float": True,
        }
        if self.action is not None:
            kwargs["action"] = self.action
        menu.add.button(self.label, **kwargs) \
                .add_draw_callback(self.draw_widget)
