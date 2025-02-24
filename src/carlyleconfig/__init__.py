import logging
from typing import Type, Any

from carlyleconfig.register import register
from carlyleconfig.environment import ConfigEnvironment


logging.getLogger(__name__).addHandler(logging.NullHandler())


def deriveconfig(Cls: Type[Any]) -> Type[Any]:
    """Decorator to place on configuration class.

    Decorate a class to register it as a configuration class with
    carlyleconfig. Any members that are of type Key will have their
    value derived at init time.

    .. code-block::

        from carlyleconfig import deriveconfig, derive

        @deriveconfig
        class Config:
            value: str
            derived_value: str = (
                derive.field()
                .from_env_var("ENV_VAR")
                .from_constant("default")
            )

    """
    register(Cls)
    return Cls


derive = ConfigEnvironment()


__all__ = [
    "deriveconfig",
    "derive",
    "ConfigEnvironment",
]
