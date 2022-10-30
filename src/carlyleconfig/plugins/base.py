from abc import ABC
from typing import ClassVar
from dataclasses import dataclass

from carlyleconfig.key import ConfigKey


@dataclass
class BasePlugin(ABC):
    factory_name: ClassVar[str]

    def inject_factory_method(self, key: ConfigKey):
        raise NotImplementedError("inject_factory_method")

    @property
    def provider_name(self) -> str:
        raise NotImplementedError("provider_name")

    @classmethod
    def name(cls):
        return cls.__name__
