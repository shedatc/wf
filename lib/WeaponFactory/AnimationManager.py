from json    import loads as json_load
from os.path import basename

from .Animation      import Animation
from .AnimationClock import AnimationClock
from .AnimationFrame import AnimationFrame
from .assets         import Assets
from .utils          import Config, log_ex

class AnimationManager:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, sprite_name):
        self.current    = None
        self.animations = {}

        path = Assets.locate("sprite", f"{sprite_name}.json")
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
            AnimationClock.singleton().register_animation(a)
        self.select("Idle")

    def _load_spritesheet_libresprite(self, conf):
        meta    = conf["meta"]
        app     = meta["app"]
        version = meta["version"]
        format  = meta["format"]
        image   = meta["image"]
        AnimationManager.log(f"Application: {app}")
        AnimationManager.log(f"Version:     {version}")
        AnimationManager.log(f"Format:      {format}")

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
            AnimationManager.log(f"Animation '{name}':")
            AnimationManager.log(f"    Direction: {direction}")
            AnimationManager.log(f"    Frames:    {start}..{end}")

            frames = []
            for f in range(start, end+1):
                frame           = conf["frames"][f]
                animation_frame = AnimationFrame(self.surface,
                                                 frame["frame"]["x"],
                                                 frame["frame"]["y"],
                                                 frame["frame"]["w"],
                                                 frame["frame"]["h"],
                                                 duration=frame["duration"])
                frames.append(animation_frame)

            self.animations[name] = Animation(name, frames)

    def select(self, name):
        if self.current is not None:
            AnimationClock.singleton().pause_animation(self.current)
        self.current = self.animations[name]
        self.current.rewind()
        AnimationClock.singleton().resume_animation(self.current)
        AnimationManager.log(f"Selected animation: {name}")

    def pause(self):
        assert self.current is not None
        AnimationClock.singleton().pause_animation(self.current)
        AnimationManager.log(f"Paused animation: {self.current.name}")

    def resume(self):
        assert self.current is not None
        AnimationClock.singleton().resume_animation(self.current)
        AnimationManager.log(f"Resumed animation: {self.current.name}")

    def name(self):
        assert self.current is not None
        f = self.current
        return f"{f.name}[{f.current}]"

    def blit_current_at(self, surface, x, y):
        if self.current is None:
            return
        self.current.blit_at(surface, x, y)

        if False:
            if Config.singleton().must_log("Animation"):
                # FIXME
                # pyxel.text(x + 20, y + 1, f"A: {self.current.name}", 0)
                raise NotImplementedError("Must replace pyxel.text")
