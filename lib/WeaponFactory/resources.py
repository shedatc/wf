import json
import os
import os.path
import pygame

from os      import getcwd, getenv
from os.path import join           as pjoin
from pprint  import pprint

from .utils import Config, log_ex

class Resources:

    _singleton = None

    @classmethod
    def log(cls, msg):
        log_ex(msg, category="Resources")

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = Resources()
        return cls._singleton

    @classmethod
    def _dir(cls):
        wf_data_dir = getenv("WF_DATA")
        if wf_data_dir is not None:
            return wf_data_dir
        xdg_data_home_dir = getenv("XDG_DATA_HOME")
        if xdg_data_home_dir is not None:
            return pjoin(xdg_data_home_dir, "wf")
        home_dir = getenv("HOME")
        assert home_dir is not None, "Missing HOME environment variable"
        return pjoin(home_dir, ".local", "share", "wf")

    @classmethod
    def locate(cls, resource_type, file_name):
        rt_dirs = Config.singleton().get("resources.json", resource_type)
        if rt_dirs is None:
            raise RuntimeError(f"Invalid resource type: {resource_type}")
        for d in rt_dirs:
            if d[0] == "/":
                path = os.path.join(d, file_name)
            else:
                path = pjoin(Resources._dir(), d, file_name)
            if os.path.exists(path):
                return path
        else:
            Resources.log(f'Resources Base Directory: {Resources._dir()}')
            Resources.log(f'{resource_type} Directories: {rt_dirs}')
            raise RuntimeError(f"Missing {resource_type} resource: {file_name}")

    def __init__(self):
        self.images = {}

    def image(self, name):
        if name in self.images:
            return self.images[name]

        path = Resources.locate("image", name)
        if path is None:
            raise RuntimeError("Image not found")

        img               = pygame.image.load(path)
        self.images[name] = img
        Resources.log(f'Image: name="{name}" path="{path}" img={img}')
        return img
