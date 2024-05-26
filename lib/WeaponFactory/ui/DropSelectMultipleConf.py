from .WidgetConf import WidgetConf

class DropSelectMultipleConf(WidgetConf):

    def __init__(self, label, items):
        WidgetConf.__init__(self, label)
        self.items = items

    def add(self, menu):
        kwargs = {
            # "float": True,
            "items": self.items,
        }
        menu.add.dropselect_multiple(self.label, **kwargs)
