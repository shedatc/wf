from .WidgetConf import WidgetConf

class SelectorConf(WidgetConf):

    def __init__(self, label, items, selected=0, id=None, action=None):
        WidgetConf.__init__(self, label)
        self.action   = action
        self.id       = id
        self.items    = items
        self.selected = selected

    def add(self, menu):
        kwargs = {
            "float":    True,
            "items":    self.items,
            "default":  self.selected,
            "onchange": self.action,
        }
        if self.id is not None:
            kwargs["selector_id"] = self.id
        menu.add.selector(self.label + " ", **kwargs) \
                .add_draw_callback(self.draw_widget)
