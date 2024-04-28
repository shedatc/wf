from json import loads as json_load

from os.path import basename
from os.path import join as path_join

from pygame       import Rect
from pygame.image import load as image_load

from .Animation      import Animation
from .AnimationFrame import AnimationFrame
from .Assets         import Assets
from .utils          import log_ex

class AnimationFactory:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    @classmethod
    def _load_spritesheet_libresprite(cls, conf):
        meta    = conf["meta"]
        app     = meta["app"]
        version = meta["version"]
        format  = meta["format"]
        image   = meta["image"]

        AnimationFactory.log(f"Application: {app}")
        AnimationFactory.log(f"Version:     {version}")
        AnimationFactory.log(f"Format:      {format}")

        if version != "1.0":
            raise RuntimeError("Libresprite spritesheet version not supported")
        if format not in ["I8", "RGBA8888"]:
            raise RuntimeError("Libresprite spritesheet format not supported")

        # Ignore all but the filename from the image path
        surface = image_load( Assets.locate("animation", basename(image)) )

        if "frameTags" not in meta:
            raise RuntimeError("Missing frameTags")
        animations = {}
        for frame_tag in meta["frameTags"]:
            name      = frame_tag["name"]
            direction = frame_tag["direction"]
            start     = frame_tag["from"]
            end       = frame_tag["to"]
            if direction != "forward":
                raise RuntimeError("Direction not supported")
            frames = []
            for f in range(start, end+1):
                frame           = conf["frames"][f]
                frame_rect = Rect((frame["frame"]["x"], frame["frame"]["y"]),
                                  (frame["frame"]["w"], frame["frame"]["h"]))
                animation_frame = AnimationFrame(f"{name} {f}/{end}",
                                                 surface,
                                                 frame_rect,
                                                 duration=frame["duration"])
                frames.append(animation_frame)

            AnimationFactory.log(f"Animation '{name}':")
            AnimationFactory.log(f"    Direction: {direction}")
            AnimationFactory.log(f"    Frames:    {start}..{end}, {len(frames)} frames")

            animations[name] = Animation(name, frames)

        return (surface, animations)

    def __init__(self):
        self._animations = {}
        self.load_count  = 0

    def load(self, group_name):
        if group_name in self._animations:
            AnimationFactory.log(f"Copying animation group '{group_name}'…")
            (surface, animations) = self._animations[group_name]
            animations_copy       = {}
            for name, animation in animations.items():
                animations_copy[name] = animation.copy()
            return (surface, animations_copy)

        conf_path = Assets.locate("animation", group_name + ".json")
        AnimationFactory.log(f"Loading animation group '{group_name}' from {conf_path}…")
        with open(conf_path, "r") as cf:
            conf = json_load( cf.read() )
        spritesheet_load = None
        if "meta" in conf and "app" in conf["meta"]:
            app = conf["meta"]["app"]
            if app == "https://github.com/LibreSprite/LibreSprite/":
                spritesheet_load = AnimationFactory._load_spritesheet_libresprite
        if spritesheet_load is None:
            raise RuntimeError("No loader for spritesheet")
        (surface, animations) = spritesheet_load(conf)
        assert surface is not None, "Missing surface"
        assert len(animations) > 0, "Missing animations"
        self._animations[group_name] = (surface, animations)
        self.load_count += 1

        return (surface, animations)
