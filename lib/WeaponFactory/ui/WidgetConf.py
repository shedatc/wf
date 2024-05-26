from ..utils import log_ex

class WidgetConf:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, label):
        self.label = label

    def draw_widget(self, widget, menu):
        widgets  = menu.get_widgets()
        selected = 0
        for i, widget in enumerate(widgets):
            if widget.is_selected():
                selected = i

        def get_height_sum(w):
            h = 0
            for i, widget in enumerate(widgets):
                if i == w:
                    break
                h += widget.get_height()
            return h

        for i, widget in enumerate(widgets):
            if i < selected:
                y = -get_height_sum(selected - i)
            else:
                y = get_height_sum(i - selected)
            widget.translate(0, y)

    def add(self, menu):
        raise NotImplementedError()
