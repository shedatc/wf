from .AnimationState import AnimationState

class Animation:

    def __init__(self, name, frames, is_loop=True):
        self._frames  = frames
        self._state   = AnimationState(frames, is_loop)
        self.name     = name

    def __repr__(self):
        return f"<Animation '{self.name}' at frame '{self._cf().name}'>"

    def set_loop(self, enable):
        self._state.is_loop = enable

    # Current Frame
    def _cf(self):
        return self._frames[self._state.current_frame_index]

    # Get a copy of the animation but without its state.
    def copy(self):
        return Animation(self.name, self._frames, is_loop=self._state.is_loop)

    def rewind(self):
        self._state.rewind()
        return self

    def pause(self):
        self._state.pause()
        return self

    def resume(self):
        self._state.resume()
        return self

    def blit_at(self, position):
        if self._state.is_done():
            return
        self._cf().blit_at(position)
