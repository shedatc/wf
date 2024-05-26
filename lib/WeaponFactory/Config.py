from json    import loads as json_loads
from json    import dumps as json_dumps
from os      import getenv
from os.path import join as path_join
from sys     import stderr

class Config:

    _singleton = None

    @classmethod
    def singleton(cls):
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def _dir(cls):
        wf_conf_dir = getenv("WF_CONF")
        if wf_conf_dir is not None:
            return wf_conf_dir
        xdg_config_home_dir = getenv("XDG_CONFIG_HOME")
        if xdg_config_home_dir is not None:
            return path_join(xdg_config_home_dir, "wf")
        home_dir = getenv("HOME")
        assert home_dir is not None, "Missing HOME environment variable"
        return path_join(home_dir, ".config", "wf")

    def __init__(self):
        self._index = {}
        # self._load_log_categories()

    def load(self, file_name):
        if file_name not in self._index:
            path = path_join(Config._dir(), file_name)
            print(f"- Config - Loading {path}…", file=stderr)
            with open(path, "r") as cf:
                self._index[file_name] = json_loads(cf.read())
        return self._index[file_name]

    def save(self, file_name):
        assert file_name in self._index
        config = self._index[file_name]
        path   = path_join(Config._dir(), file_name)
        print(f"- Config - Saving {path}…", file=stderr)
        with open(path, "w") as cf:
            cf.write( json_dumps(config) )

    def get(self, file_name, key, default=None):
        config = self.load(file_name)
        if key in config:
            return config[key]
        else:
            return default

    def get_log_categories(self):
        return self.load("engine.json")["logs"]

    def must_log(self, category):
        return self.get_log_categories()[category]
