from .EngineClock import EngineClock
from .utils       import log_ex

class AnimationState:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, frames, is_loop):
        self._is_loop            = is_loop
        self._last_frame_index   = len(frames) - 1
        self.current_frame_index = 0

        self._duration  = frames[0].duration # Remaining duration of the current frame.
        self._durations = []                 # Store the duration of each frame.
        for f in frames:
            self._durations.append( f.duration )

        EngineClock.singleton().register(self)

    def __str__(self):
        return f"<AnimationState {self.current_frame_index} in 0..{self._last_frame_index}>"

    def __del__(self):
        EngineClock.singleton().unregister(self)

    def rewind(self):
        AnimationState.log(f"Rewinding…")
        self.current_frame_index    = 0
        self._duration = self._durations[0]

    def pause(self):
        EngineClock.singleton().pause(self)

    def resume(self):
        EngineClock.singleton().resume(self)

    def _next_frame(self):
        assert not self.is_done()
        self.current_frame_index += 1
        if self.current_frame_index <= self._last_frame_index:
            self._duration = self._durations[self.current_frame_index]
        elif self._is_loop: # and self.current_frame_index > self._last_frame_index
            self.rewind()
        AnimationState.log(f"Now at frame {self.current_frame_index}/{self._last_frame_index}")

    def is_done(self):
        return self.current_frame_index > self._last_frame_index and not self._is_loop

    # Add time to the current frame. If adding more time than necessary to
    # finish it, use this time for the next frame, etc…
    def add_time(self, t):
        assert not self.is_done()
        while t > 0 and not self.is_done():
            AnimationState.log(f"Adding {t} ms to frame {self.current_frame_index}/{self._last_frame_index}")

            assert self._duration > 0
            orig_remaining_duration = self._duration
            if t <= self._duration:
                self._duration -= t
                t                            = 0
            else: # t > self._duration
                t                           -= self._duration
                self._duration  = 0

            AnimationState.log(f"Added {t} ms to current frame:")
            AnimationState.log(f"    {orig_remaining_duration} → {self._duration} ms")
            AnimationState.log(f"{t} ms remaining")

            if self._duration == 0:
                self._next_frame()
        if self.is_done():
            AnimationState.log(f"Animation done")
