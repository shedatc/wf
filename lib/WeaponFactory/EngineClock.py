import pygame

from .utils import Config, log_ex

class EngineClock:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self):
        config    = Config.singleton().load("engine.json")
        self._fps = config["fps"]
        EngineClock.log(f"FPS: {self._fps}")
        self._running_animations = []
        self._paused_animations  = []
        self.reset_clock()

    def reset_clock(self):
        self.clock = pygame.time.Clock()
        EngineClock.log(f"Reset")

    def register_animation(self, animation):
        assert animation not in self._running_animations
        assert animation not in self._paused_animations
        self._paused_animations.append(animation)
        EngineClock.log(f"Registered paused animation: {animation.name}")

    def unregister_animation(self, animation):
        if animation in self._running_animations:
            self._running_animations.remove(animation)
            EngineClock.log(f"Unregistered running animation: {animation.name}")
        elif animation in self._paused_animations:
            self._paused_animations.remove(animation)
            EngineClock.log(f"Unregistered paused animation: {animation.name}")
        else:
            raise AssertionError("Unknown animation")

    def pause_animation(self, animation):
        self._running_animations.remove(animation)
        self._paused_animations.append(animation)
        EngineClock.log(f"Paused animation: {animation.name}")

    def resume_animation(self, animation):
        self._paused_animations.remove(animation)
        self._running_animations.append(animation)
        EngineClock.log(f"Resumed animation: {animation.name}")

    # Add time to running animations and return time (ms) since previous tick.
    def tick(self):
        t = self.clock.tick(self._fps)
        EngineClock.log(f"Tick: {t} ms since previous tick")
        c = 0
        for a in self._running_animations:
            a.add_time(t)
            if a.is_done():
                self.pause_animation(a)
            c += 1
        EngineClock.log(f"Added {t} ms to {c} animations")
        return t
