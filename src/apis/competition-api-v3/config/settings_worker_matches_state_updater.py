from copy import deepcopy

from .settings import *  # noqa

LOGGING = deepcopy(LOGGING or {})  # noqa

try:
    LOGGING["handlers"]["loki"]["tags"][
        "application"
    ] += "-worker-matches-state-updater"
    LOGGING["root"]["handlers"] = ["console", "loki"]
except KeyError:
    pass
