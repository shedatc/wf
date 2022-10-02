import inspect
import json

from os      import getcwd, getenv
from os.path import join   as pjoin
from sys     import stderr
from time    import time

log_previous_time = None

def log_ex(msg, category=None, name=None):
    if category is not None and not Config.singleton().must_log(category):
        return

    tokens = []

    global log_previous_time
    t = time()
    if log_previous_time is not None:
        dt = t - log_previous_time
        tokens.append("{:.5f}".format(dt))
    else:
        tokens.append("-")
    log_previous_time = t

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

def log_current_context():
    f = inspect.currentframe().f_back
    msg = f"In file {f.f_code.co_filename} at line {f.f_lineno}"
    log_ex(msg)

def sz(size):
    (w, h) = size
    return f"{w}x{h}"

class Config:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = Config()
        return cls._singleton

    @classmethod
    def _dir(cls):
        wf_conf_dir = getenv("WF_CONF")
        if wf_conf_dir is not None:
            return wf_conf_dir
        xdg_config_home_dir = getenv("XDG_CONFIG_HOME")
        if xdg_config_home_dir is not None:
            return pjoin(xdg_config_home_dir, "wf")
        home_dir = getenv("HOME")
        assert home_dir is not None, "Missing HOME environment variable"
        return pjoin(home_dir, ".config", "wf")

    def __init__(self):
        self._index          = {}
        self._log_categories = None

    def load(self, file_name):
        if file_name not in self._index:
            path = pjoin(Config._dir(), file_name)
            log_ex(f"Configuration: {path}")
            with open(path, "r") as cf:
                self._index[file_name] = json.loads(cf.read())
        return self._index[file_name]

    def get(self, file_name, key, default=None):
        config = self.load(file_name)
        if key in config:
            return config[key]
        else:
            return default

    def get_log_categories(self):
        if self._log_categories is None:
            self._log_categories = list(map(lambda s: s.lower(),
                                            self.get("engine.json", "logs", default=[])))
        return self._log_categories

    def must_log(self, category):
        return category.lower() in self.get_log_categories()

class Observable:

    def __init__(self):
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)


    # Observer must implement the following:
    #     def notify(self, event, observable, **kwargs)
    def notify_observers(self, event, **kwargs):
        for o in self.observers:
            o.notify(event, self, **kwargs)
