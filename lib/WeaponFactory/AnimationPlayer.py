from .AnimationFactory import AnimationFactory
from .utils            import log_ex

class AnimationPlayer:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, group_name, select="Idle", enable=False, is_loop=True):
        self._current = None
        self.visible  = False

        (self.surface, self.animations) = AnimationFactory.singleton().load(group_name)
        for _, a in self.animations.items():
            a.set_loop(is_loop)
        self.current = self.animations[select]
        if enable:
            self.current.resume()
            AnimationPlayer.log(f"Now playing animation '{select}'")

    def show(self):
        self.visible = True
        return self

    def hide(self):
        self.visible = False
        return self

    def select(self, name):
        orig_name = None
        if self._current is not None:
            orig_name = self.current.name
            self._current.pause()
        self.current = self.animations[name].rewind().resume()
        if orig_name is None:
            AnimationPlayer.log(f"Now playing animation '{name}'")
        else:
            AnimationPlayer.log(f"Now playing animation '{orig_name}' → '{name}'")
        return self

    def pause(self):
        self.current.pause()
        return self

    def resume(self):
        self.current.resume()
        return self

    def blit_at(self, position):
        if not self.visible:
            return
        self.current.blit_at(position)
