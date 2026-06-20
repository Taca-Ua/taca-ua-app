from copy import deepcopy

from .settings import *  # noqa

LOGGING = deepcopy(LOGGING or {})  # noqa

try:
    LOGGING["handlers"]["loki"]["tags"]["application"] += "-projection-updater"
    LOGGING["root"]["handlers"] = ["console", "loki"]
except KeyError:
    pass
