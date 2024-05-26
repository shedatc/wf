from .SelectorConf import SelectorConf

class CheckboxConf(SelectorConf):

    def __init__(self, label, enable=False, action=None, id=None):
        if enable:
            selected = 0
        else:
            selected = 1
        SelectorConf.__init__(self,
                              label,
                              [("On", True), ("Off", False)],
                              selected=selected,
                              action=action,
                              id=id)
