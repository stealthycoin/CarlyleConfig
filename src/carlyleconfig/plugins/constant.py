import logging
from dataclasses import dataclass
from typing import Any, ClassVar
from types import MethodType

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey


LOG = logging.getLogger(__name__)


@dataclass
class ConstantProvider:
    value: Any

    def provide(self) -> Any:
        LOG.debug("Providing: %s", self.value)
        return self.value


def with_constant(self, value: Any) -> ConfigKey:
    self.providers.append(ConstantProvider(value))
    return self


@dataclass
class ConstantPlugin(BasePlugin):
    factory_name: ClassVar[str] = "constant"

    def inject_factory_method(self, key: ConfigKey) -> ConfigKey:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(with_constant, key))
        return key
