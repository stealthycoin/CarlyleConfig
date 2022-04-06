from carlyleconfig.register import register
from carlyleconfig.environment import ConfigEnvironment


def deriveconfig(Cls):
    register(Cls)
    return Cls


derive = ConfigEnvironment()


__all__ = [
    "deriveconfig",
    "derive",
    "ConfigEnvironment",
]
