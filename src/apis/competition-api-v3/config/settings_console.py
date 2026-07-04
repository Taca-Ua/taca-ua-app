from copy import deepcopy

from .settings import *  # noqa

LOGGING = deepcopy(LOGGING or {})  # noqa

try:
    LOGGING["handlers"]["loki"]["tags"]["application"] += "-events-publisher"
    LOGGING["root"]["handlers"] = ["console"]
except KeyError:
    pass
