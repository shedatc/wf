import inspect

from sys  import stderr
from time import time

from .Config import Config

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
