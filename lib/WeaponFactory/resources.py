import json
import os
import os.path
import pyxel

from pprint import pprint

from .utils import Config, logEx

class Resources:

    singleton = None

    def log(msg):
        logEx(msg, category="Resources", frame=False)

    def __init__(self):
        assert Resources.singleton is None
        Resources.singleton = self

        self.nextImg = 1
        self.images  = {}

    def locateResource(self, resourceType, fileName):
        for d in Config.get("resources.json", resourceType):
            if d[0] == "/":
                path = os.path.join(d, fileName)
            else:
                path = os.path.join(os.getcwd(), d, fileName)
            if os.path.exists(path):
                return path
        else:
            return None

    def image(name):
        assert Resources.singleton is not None
        self = Resources.singleton

        if name in self.images:
            return self.images[name]
        elif self.nextImg >= 3:
            raise RuntimeError("images pool exhausted")

        path = self.locateResource("image", f"{name}.png")
        if path is None:
            raise RuntimeError("image not found")

        img = self.nextImg
        pyxel.image(img).load(0, 0, path)
        self.images[name] = img
        Resources.log(f'Image: name="{name}" path="{path}" img={img}')
        self.nextImg += 1
        return img
