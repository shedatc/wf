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
        self._running = []
        self._paused  = []
        self.reset_clock()

    def reset_clock(self):
        self.clock = pygame.time.Clock()
        EngineClock.log(f"Reset")

    def register(self, task):
        assert task not in self._running
        assert task not in self._paused
        self._paused.append(task)
        EngineClock.log(f"Registered paused task: {task}")

    def unregister(self, task):
        if task in self._running:
            self._running.remove(task)
            EngineClock.log(f"Unregistered running task: {task}")
        elif task in self._paused:
            self._paused.remove(task)
            EngineClock.log(f"Unregistered paused task: {task}")
        else:
            raise AssertionError("Unknown task")

    def pause(self, task):
        self._running.remove(task)
        self._paused.append(task)
        EngineClock.log(f"Paused task: {task}")

    def resume(self, task):
        self._paused.remove(task)
        self._running.append(task)
        EngineClock.log(f"Resumed task: {task}")

    # Add time to running animations and return time (ms) since previous tick.
    def tick(self):
        t = self.clock.tick(self._fps)
        EngineClock.log(f"Tick: {t} ms since previous tick")
        c = 0
        for task in self._running:
            task.add_time(t)
            if task.is_done():
                self.pause(task)
            c += 1
        EngineClock.log(f"Added {t} ms to {c} tasks")
        return t
