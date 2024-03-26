
from os           import getenv
from os.path      import exists as path_exists
from os.path      import join   as path_join
from pygame.image import load as image_load

from .Config import Config
from .utils  import log_ex

class Assets:

    _singleton = None

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = Assets()
        return cls._singleton

    @classmethod
    def _dir(cls):
        wf_data_dir = getenv("WF_DATA")
        if wf_data_dir is not None:
            return wf_data_dir
        xdg_data_home_dir = getenv("XDG_DATA_HOME")
        if xdg_data_home_dir is not None:
            return path_join(xdg_data_home_dir, "wf")
        home_dir = getenv("HOME")
        assert home_dir is not None, "Missing HOME environment variable"
        return path_join(home_dir, ".local", "share", "wf")

    @classmethod
    def locate(cls, asset_type, file_name):
        rt_dirs = Config.singleton().get("assets.json", asset_type)
        if rt_dirs is None:
            raise RuntimeError(f"Invalid asset type: {asset_type}")
        for d in rt_dirs:
            if d[0] == "/":
                path = path_join(d, file_name)
            else:
                path = path_join(Assets._dir(), d, file_name)
            if path_exists(path):
                return path
        else:
            Assets.log(f'Assets Base Directory: {Assets._dir()}')
            Assets.log(f'{asset_type} Directories: {rt_dirs}')
            raise RuntimeError(f"Missing {asset_type} asset: {file_name}")

    def __init__(self):
        self.images = {}

    @classmethod
    def image(cls, name):
        self = cls.singleton()
        if name in self.images:
            return self.images[name]

        path = Assets.locate("image", name)
        if path is None:
            raise RuntimeError("Image not found")

        img               = image_load(path)
        self.images[name] = img
        Assets.log(f"Image:")
        Assets.log(f"    Name: {name}")
        Assets.log(f"    Path: {path}")
        return img
