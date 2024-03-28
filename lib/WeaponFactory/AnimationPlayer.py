from json    import loads as json_load
from os.path import basename
from pygame  import Rect

from .Animation      import Animation
from .AnimationFrame import AnimationFrame
from .Assets         import Assets
from .Config         import Config
from .EngineClock    import EngineClock
from .utils          import log_ex

class AnimationPlayer:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, animation_name, select="Idle"):
        self.current    = None
        self.animations = {}

        path = Assets.locate("animation", f"{animation_name}.json")
        with open(path, "r") as cf:
            conf             = json_load(cf.read())
            spritesheet_load = None
            if "meta" in conf and "app" in conf["meta"]:
                app = conf["meta"]["app"]
                if app == "https://github.com/LibreSprite/LibreSprite/":
                    spritesheet_load = self._load_spritesheet_libresprite
            if spritesheet_load is None:
                raise RuntimeError("No loader for spritesheet")
            spritesheet_load(conf)
            assert self.surface is not None, "Missing surface"
            assert len(self.animations) > 0, "Missing animations"

        for a in self.animations.values():
            EngineClock.singleton().register(a)
        self.select(select)

    def _load_spritesheet_libresprite(self, conf):
        meta    = conf["meta"]
        app     = meta["app"]
        version = meta["version"]
        format  = meta["format"]
        image   = meta["image"]
        AnimationPlayer.log(f"Application: {app}")
        AnimationPlayer.log(f"Version:     {version}")
        AnimationPlayer.log(f"Format:      {format}")

        if version != "1.0":
            raise RuntimeError("Libresprite spritesheet version not supported")
        if format != "I8":
            raise RuntimeError("Libresprite spritesheet format not supported")

        # Ignore all but the filename from the image path
        self.surface = Assets.image( basename(image) )

        if "frameTags" not in meta:
            raise RuntimeError("Missing frameTags")
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
                                                 self.surface,
                                                 frame_rect,
                                                 duration=frame["duration"])
                frames.append(animation_frame)

            AnimationPlayer.log(f"Animation '{name}':")
            AnimationPlayer.log(f"    Direction:   {direction}")
            AnimationPlayer.log(f"    Frames:      {start}..{end}, {len(frames)} frames")

            self.animations[name] = Animation(name, frames)

    def select(self, name):
        if self.current is not None:
            EngineClock.singleton().pause(self.current)
        self.current = self.animations[name]
        self.current.rewind()
        EngineClock.singleton().resume(self.current)
        AnimationPlayer.log(f"Selected animation: {name}")

    def pause(self):
        assert self.current is not None
        EngineClock.singleton().pause(self.current)
        AnimationPlayer.log(f"Paused animation: {self.current.name}")

    def resume(self):
        assert self.current is not None
        EngineClock.singleton().resume(self.current)
        AnimationPlayer.log(f"Resumed animation: {self.current.name}")

    def name(self):
        assert self.current is not None
        f = self.current
        return f"{f.name}[{f.current}]"

    def blit_current_at(self, position):
        if self.current is None:
            return
        self.current.blit_at(position)

        if False:
            if Config.singleton().must_log("Animation"):
                # FIXME
                # pyxel.text(x + 20, y + 1, f"A: {self.current.name}", 0)
                raise NotImplementedError("Must replace pyxel.text")
