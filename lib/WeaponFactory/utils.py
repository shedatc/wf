import inspect
import json
import pyxel

from os      import getcwd, getenv
from os.path import join   as pjoin
from sys     import stderr
from time    import time

logPreviousTime = None

def logEx(msg, category=None, name=None, frame=True):
    if category is not None and not Config.mustLog(category):
        return

    tokens = []

    global logPreviousTime
    t = time()
    if logPreviousTime is not None:
        dt = t - logPreviousTime
        tokens.append("{:.5f}".format(dt))
    else:
        tokens.append("-")
    logPreviousTime = t

    if frame:
        tokens.append(str(pyxel.frame_count))
    else:
        tokens.append("-")

    if category is not None:
        tokens.append(category)
    else:
        tokens.append("-")

    if name is not None:
        tokens.append(name)
    else:
        tokens.append("-")

    tokens.append(msg)

    print(" ".join(tokens), file=stderr)

def logCurrentContext():
    f = inspect.currentframe().f_back
    msg = f"In file {f.f_code.co_filename} at line {f.f_lineno}"
    logEx(msg)

class Config:

    singleton = None

    def getSingleton():
        if Config.singleton is None:
            Config.singleton = Config()
        return Config.singleton

    def load(fileName):
        self = Config.getSingleton()

        if fileName not in self.index:
            baseDir = getenv("WF_CONF", pjoin(getcwd(), "etc"))
            path    = pjoin(baseDir, fileName)
            logEx(f'Configuration: {path}', category=None, frame=False)
            with open(path, "r") as cf:
                self.index[fileName] = json.loads(cf.read())
        return self.index[fileName]

    def get(fileName, key, default=None):
        config = Config.load(fileName)
        if key in config:
            return config[key]
        else:
            return default

    def __init__(self):
        assert Config.singleton is None
        Config.singleton   = self
        self.index         = {}
        self.logCategories = None

    def getLogCategories(self):
        if self.logCategories is None:
            self.logCategories = list(map(lambda s: s.lower(),
                                          Config.get("engine.json", "logs", default=[])))
        return self.logCategories

    def mustLog(category):
        return category.lower() in Config.getSingleton().getLogCategories()

class Observable:

    def __init__(self):
        self.observers = []

    def registerObserver(self, observer):
        self.observers.append(observer)


    # Observer must implement the following:
    #     def notify(self, event, observable, **kwargs)
    def notifyObservers(self, event, **kwargs):
        for o in self.observers:
            o.notify(event, self, **kwargs)
