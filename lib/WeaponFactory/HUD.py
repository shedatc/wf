from pygame       import Rect
from pygame.image import load as image_load

from .Assets import Assets
from .Config import Config
from .Screen import Screen
from .utils  import log_ex

class HUD:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            HUD()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        config = Config.singleton().load(f"HUD.json")
        image  = "HUD.png"
        if "image" in config:
            image = config["image"]
        self._surface = image_load( Assets.locate("image", image) )
        self._selected = Rect((config["selected"]["x"], config["selected"]["y"]),
                              (config["selected"]["w"], config["selected"]["h"]))

        HUD._singleton = self

    def blit_selected(self, position):
        rect        = self._selected.copy()
        rect.center = position
        Screen.singleton().blit(self._surface, rect.topleft, source_rect=self._selected)
