import pygame

from .Config import Config
from .utils  import log_ex

class EngineClock:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def delete_singleton(cls):
        cls._singleton = None

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
        assert task not in self._running, "Task already registered and currently running"
        assert task not in self._paused, "Task already registered and currently paused"
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
        try:
            self._running.remove(task)
        except ValueError:
            assert task in self._paused, "Trying to pause a task that was not running"
        if task not in self._paused:
            self._paused.append(task)
            EngineClock.log(f"Paused task: {task}")
        else:
            EngineClock.log("Trying to pause a task that is already paused")

    def resume(self, task):
        try:
            self._paused.remove(task)
        except ValueError:
            assert task in self._running, "Trying to resume a task that was not paused"
        if task not in self._running:
            self._running.append(task)
            EngineClock.log(f"Resumed task: {task}")
        else:
            EngineClock.log("Trying to resume a task that is already running")

    # Add time to running tasks and return time (ms) since previous tick.
    def tick(self):
        if self._fps == 0:
            t = self.clock.tick()
        else:
            t = self.clock.tick(self._fps)
        if len(self._running) == 0:
            return t
        EngineClock.log(f"Tick: {t} ms since previous tick")
        c = 0
        for task in self._running:
            task.add_time(t)
            EngineClock.log(f"Added {t} ms to task {task}")
            if task.is_done():
                self.pause(task)
            c += 1
        if c > 0:
            EngineClock.log(f"Added {t} ms to {c} tasks")
        return t

    def fps(self):
        return self.clock.get_fps()

    def running_task_count(self):
        return len(self._running)

    def paused_task_count(self):
        return len(self._paused)
