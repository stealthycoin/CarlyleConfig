import logging
from dataclasses import dataclass
from typing import Any, Callable, ClassVar
from types import MethodType

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey


LOG = logging.getLogger(__name__)


@dataclass
class DefaultFactoryProvider:
    fn: Callable[[], Any]

    @property
    def description(self) -> str:
        return f"defaults to result of function {self.fn.__name__}"

    def provide(self) -> Any:
        value = self.fn()
        LOG.debug("Providing: %s", value)
        return value


def with_default_factory(self: ConfigKey, fn: Callable[[], Any]) -> ConfigKey:
    self.providers.append(DefaultFactoryProvider(fn))
    return self


@dataclass
class DefaultFactoryPlugin(BasePlugin):
    factory_name: ClassVar[str] = "default_factory"

    @property
    def provider_name(self) -> str:
        return "DefaultFactoryProvider"

    def inject_factory_method(self, key: ConfigKey) -> None:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(with_default_factory, key))
