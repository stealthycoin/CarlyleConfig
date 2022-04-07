import logging

from carlyleconfig.register import register
from carlyleconfig.environment import ConfigEnvironment


logging.getLogger(__name__).addHandler(logging.NullHandler())


def deriveconfig(Cls):
    register(Cls)
    return Cls


derive = ConfigEnvironment()


__all__ = [
    "deriveconfig",
    "derive",
    "ConfigEnvironment",
]
