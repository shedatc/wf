from math import floor

class StatCounter:

    def __init__(self):
        self.avg_len = 10
        self.current = 0
        self._values = []

    def __int__(self):
        return self.current

    def __iadd__(self, n):
        self.current += int(n)
        return self

    def __isub__(self, n):
        self.current -= int(n)
        return self

    def reset(self):
        if len(self._values) >= self.avg_len:
            self._values.pop(0)
        self._values.append(self.current)
        self.current = 0
        return self

    def avg(self):
        if len(self._values) > 0:
            return floor( sum(self._values) / len(self._values) )
        else:
            return self.current
